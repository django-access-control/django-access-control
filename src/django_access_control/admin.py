from django.contrib import admin
from django.db.models import Model, QuerySet

from .permissions import AnyModelPermission


class ConfidentialModelAdmin(admin.ModelAdmin):

    def has_change_permission(self, request, obj: Model = None) -> bool:
        return AnyModelPermission("change", self.model).is_authorized(request.user)

    def has_view_permission(self, request, obj: Model = None) -> bool:
        return AnyModelPermission("view", self.model).is_authorized(request.user)

    def get_queryset(self, request) -> QuerySet:
        return super().get_queryset(request).all().has_some_permissions(request.user)

    def get_fields(self, request, obj=None):
        """
        Hook for specifying fields.
        """
        return obj.Access.changeable_fields(request.user, obj)

    def get_readonly_fields(self, request, obj=None):
        """
        Hook for specifying fields.
        """
        return obj.Access.viewable_fields(request.user, obj)
