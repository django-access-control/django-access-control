from django.contrib import admin
from django.db.models import Model, QuerySet
from django.http import HttpRequest


class ConfidentialModelAdmin(admin.ModelAdmin):

    def has_change_permission(self, request: HttpRequest, obj: Model = None) -> bool:
        has_change_permission_for_all_objects = super().has_change_permission(request)
        changeable_objects = self.model.objects.can_change(request.user)
        # If obj is None, it is asked whether or not there are any object which can be changed
        if obj is None: return has_change_permission_for_all_objects or changeable_objects.exists()
        # If obj is not None, the change permission if asked for that specific object
        return has_change_permission_for_all_objects or changeable_objects.filter(id=obj.id).exists()

    def has_view_permission(self, request: HttpRequest, obj: Model = None) -> bool:
        has_view_permission_for_all_objects = super().has_view_permission(request)
        viewable_objects = self.model.objects.can_view(request.user)
        # If obj is None, it is asked whether or not there are any object which can be viewed
        if obj is None: return has_view_permission_for_all_objects or viewable_objects.exists()
        # If obj is not None, the view permission if asked for that specific object
        return has_view_permission_for_all_objects or viewable_objects.filter(id=obj.id).exists()

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        q = super().get_queryset(request)
        return q.can_view(request.user) | q.can_change(request.user) | q.can_delete(request.user)
