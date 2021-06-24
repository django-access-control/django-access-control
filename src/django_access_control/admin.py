from django.contrib import admin
from django.db.models import Model, QuerySet
from django.http import HttpRequest

from .permissions import AnyModelPermission


class ConfidentialModelAdmin(admin.ModelAdmin):

    def has_change_permission(self, request: HttpRequest, obj: Model = None) -> bool:
        return AnyModelPermission("change", self.model).is_authorized(request.user)

    def has_view_permission(self, request: HttpRequest, obj: Model = None) -> bool:
        return AnyModelPermission("view", self.model).is_authorized(request.user)

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        q = super().get_queryset(request).all()
        return q.can_view(request.user) | q.can_change(request.user) | q.can_delete(request.user)
