from pipetools import maybe, select_first, X, where, foreach, pipe, flatten

from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.auth.models import User
from django.db.models import AutoField, TextField, CharField, SlugField, DateField, DateTimeField, ForeignKey, BooleanField, ManyToManyField


def existing_related(model, field_name):
    "Returns objects related to any instance of `model` by `field_name`."
    field = model._meta.get_field(field_name)
    related = field.related.parent_model
    return related.objects.filter(pk__in=model.objects.values(field_name))


def filter_existing(field_name, title_=None):
    """
    Wrapper for list_filter foreign key fields to only show such related
    objects for which there are any results.
    """
    class ListFilterExisting(SimpleListFilter):
        title = title_ or field_name.replace('_', ' ').capitalize()
        parameter_name = field_name

        def lookups(self, request, model_admin):
            format = foreach([X.pk, unicode]) | tuple
            return format(existing_related(model_admin.model, field_name))

        def queryset(self, request, queryset):
            value = self.value()
            return value and queryset.filter(**{field_name: value})

    return ListFilterExisting


class SmartAdmin(admin.ModelAdmin):

    list_display_exclude = AutoField, TextField, ManyToManyField
    search_field_types = CharField, SlugField, TextField

    def __init__(self, *args, **kwargs):
        super(SmartAdmin, self).__init__(*args, **kwargs)

        if self.list_display == admin.ModelAdmin.list_display:
            self.list_display = ('__unicode__', ) + (self._get_fields(
                lambda field: type(field) not in self.list_display_exclude))

        self.date_hierarchy = (self.date_hierarchy or self.all_fields > maybe
            | select_first(type | X._in_([DateTimeField, DateField]))
            | X.name)

        self.list_filter = self.list_filter or self._get_list_filter()

        self.search_fields = self.search_fields or self._get_search_fields()
        self.raw_id_fields = self.raw_id_fields or self._get_fields(
            self.should_be_raw_id_field)

        self.filter_horizontal = self.filter_horizontal or self._get_fields(
            type | (X == ManyToManyField))

    @property
    def all_fields(self):
        return (
            self.model._meta.fields,
            self.model._meta.virtual_fields,
            self.model._meta.many_to_many,
        ) > flatten | tuple

    def _get_fields(self, cond):
        return self.all_fields > where(cond) | foreach(X.name) | tuple

    def _get_search_fields(self):
        return [
            self._get_fields(lambda f: type(f) in self.search_field_types),

            # if there are any ForeignKeys to User, we'd like to be able to
            # search by the user's last_name, username and email
            (self.all_fields > pipe
                | where(isinstance, X, ForeignKey)
                | where(X.related.parent_model | (issubclass, X, User))
                | foreach(X.name)
                | foreach(['{0}__last_name', '{0}__username', '{0}__email']))

        ] > flatten | tuple

    def _get_list_filter(self):
        field_names = self._get_fields(self.should_be_in_list_filter)
        return field_names > foreach(self._apply_filter_existing) | tuple

    def _apply_filter_existing(self, field_name):
        return (filter_existing(field_name)
            if isinstance(self.model._meta.get_field(field_name), ForeignKey)
            else field_name)

    def should_be_in_list_filter(self, field):
        choices = getattr(field, 'choices', None)
        if choices and len(choices) < 20:
            return True
        if (isinstance(field, ForeignKey) and
            existing_related(self.model, field.name).count() < 20):
            return True
        if (isinstance(field, BooleanField)):
            return True

    def should_be_raw_id_field(self, field):
        if (isinstance(field, ForeignKey) and
            field.related.parent_model._default_manager.count() > 30):
            return True
