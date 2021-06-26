from typing import List
from django.contrib import admin
from django.db.models import Model, QuerySet

from .models import all_field_names
from .utils import order_set_by_iterable


class ConfidentialModelAdmin(admin.ModelAdmin):

    def has_change_permission(self, request, obj: Model = None) -> bool:
        return self.model.objects.all().rows_with_change_permission(request.user).exists()

    def has_view_permission(self, request, obj: Model = None) -> bool:
        return self.model.objects.all().rows_with_view_permission(request.user).exists()

    def get_queryset(self, request) -> QuerySet:
        return super().get_queryset(request).all().has_some_permissions(request.user)

    def get_changible_fields(self, request, obj=None) -> List[str]:
        all_fields = all_field_names(self.model)
        if obj is None: return all_fields
        accessible_fields = self.model.objects._queryset_class().changeable_fields(request.user, obj)
        return order_set_by_iterable(accessible_fields, all_fields)

    def get_fields(self, request, obj=None) -> List[str]:
        all_fields_to_show = list(self.get_changible_fields(request)) + list(self.get_changible_fields(request))
        return order_set_by_iterable(all_fields_to_show, all_field_names(self.model))

    def get_readonly_fields(self, request, obj=None) -> List[str]:
        if obj is None: return []
        viewable_fields = self.model.objects._queryset_class().viewable_fields(request.user, obj)
        changible_fields = self.get_changible_fields(request)
        return order_set_by_iterable(viewable_fields - changible_fields, all_field_names(self.model))
