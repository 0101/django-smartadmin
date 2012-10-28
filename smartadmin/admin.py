from pipetools import maybe, select_first, X, where, foreach

from django.contrib import admin
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

        self.search_fields = (self.search_fields or self._get_fields(
            lambda field: type(field) in self.search_field_types))

        self.raw_id_fields = (self.raw_id_fields or self._get_fields(
            self.should_be_raw_id_field))

    @property
    def all_fields(self):
        return self.model._meta.fields + self.model._meta.virtual_fields

    def _get_fields(self, cond):
        return self.all_fields > where(cond) | foreach(X.name) | tuple

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
