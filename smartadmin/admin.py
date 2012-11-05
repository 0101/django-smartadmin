from pipetools import maybe, select_first, X, where, foreach, pipe, flatten

from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models


class SmartAdmin(admin.ModelAdmin):

    list_display_exclude = models.AutoField, models.TextField
    search_field_types = models.CharField, models.SlugField, models.TextField

    def __init__(self, *args, **kwargs):
        super(SmartAdmin, self).__init__(*args, **kwargs)

        if self.list_display == admin.ModelAdmin.list_display:
            self.list_display = ('__unicode__', ) + (self._get_fields(
                lambda field: type(field) not in self.list_display_exclude))

        self.date_hierarchy = (self.date_hierarchy or self.all_fields > maybe
            | select_first(lambda field: type(field) in
                (models.DateTimeField, models.DateField))
            | X.name)

        self.list_filter = (self.list_filter or self._get_fields(
            self.should_be_in_list_filter))

        self.search_fields = self.search_fields or self._get_search_fields()
        self.raw_id_fields = (self.raw_id_fields or self._get_fields(
            self.should_be_raw_id_field))

    @property
    def all_fields(self):
        return self.model._meta.fields + self.model._meta.virtual_fields

    def _get_fields(self, cond):
        return self.all_fields > where(cond) | foreach(X.name) | tuple

    def _get_search_fields(self):
        return [
            self._get_fields(lambda f: type(f) in self.search_field_types),

            # if there are any ForeignKeys to User, we'd like to be able to
            # search by the user's last_name, username and email
            (self.all_fields > pipe
                | where(isinstance, X, models.ForeignKey)
                | where(X.related.parent_model | (issubclass, X, User))
                | foreach(X.name)
                | foreach(['{0}__last_name', '{0}__username', '{0}__email']))

        ] > flatten | tuple

    def should_be_in_list_filter(self, field):
        choices = getattr(field, 'choices', None)
        if choices and len(choices) < 20:
            return True
        if (isinstance(field, models.ForeignKey) and
            field.related.parent_model._default_manager.count() < 20):
            return True
        if (isinstance(field, models.BooleanField)):
            return True

    def should_be_raw_id_field(self, field):
        if (isinstance(field, models.ForeignKey) and
            field.related.parent_model._default_manager.count() > 30):
            return True
