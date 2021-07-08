from typing import List
from django.contrib import admin
from django.db.models import Model, QuerySet
from django.apps import apps

from .models import all_field_names
from .utils import order_set_by_iterable
from .querysets import is_confidential


class ConfidentialModelAdmin(admin.ModelAdmin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.permissions = self.model.objects._queryset_class()
        self.all_fields = all_field_names(self.model)

    def has_add_permission(self, request) -> bool:
        return self.permissions.has_table_wide_add_permission(request.user)

    def has_change_permission(self, request, obj: Model = None) -> bool:
        rows_with_change_permission = self.model.objects.all().rows_with_change_permission(request.user)
        return rows_with_change_permission.contains(obj) if obj else rows_with_change_permission.exists()

    def has_view_permission(self, request, obj: Model = None) -> bool:
        rows_with_view_permission = self.model.objects.all().rows_with_view_permission(request.user)
        return rows_with_view_permission.contains(obj) if obj else rows_with_view_permission.exists()

    def get_queryset(self, request) -> QuerySet:
        return super().get_queryset(request).all().rows_with_some_permission(request.user)

    def get_addable_fields(self, request) -> List[str]:
        return order_set_by_iterable(self.permissions.addable_fields(request.user), self.all_fields)

    def get_changeable_fields(self, request, obj) -> List[str]:
        return order_set_by_iterable(self.permissions.changeable_fields(request.user, obj), self.all_fields)

    def get_fields(self, request, obj=None) -> List[str]:
        if not obj:
            fields_to_show = self.get_addable_fields(request)
        else:
            viewable_fields = self.permissions.viewable_fields(request.user, obj)
            print("Viewable", viewable_fields)
            changible_fields = self.permissions.changeable_fields(request.user, obj)
            print("Changible", changible_fields)
            fields_to_show = changible_fields | viewable_fields
        return order_set_by_iterable(fields_to_show, self.all_fields)

    def get_readonly_fields(self, request, obj=None) -> List[str]:
        if obj is None : return []
        viewable_fields = self.permissions.viewable_fields(request.user, obj)
        changible_fields = self.permissions.changeable_fields(request.user, obj)
        return order_set_by_iterable(viewable_fields - changible_fields, all_field_names(self.model))

    def has_module_permission(self, request):
        app_models = list(apps.get_app_config(self.opts.app_label).get_models())
        confidential_models = {m for m in app_models if is_confidential(m)}
        return any({m.objects.all().has_some_permissions(request.user) for m in confidential_models})
