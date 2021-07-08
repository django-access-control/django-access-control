from __future__ import annotations

from typing import FrozenSet

from django.contrib.auth.models import AbstractUser
from django.db.models import QuerySet, Model

from .models import all_field_names

from .permissions import has_permission


class ConfidentialQuerySet(QuerySet):

    # Table wide permissions

    def has_table_wide_add_permission(self, user: AbstractUser) -> bool:
        return user.is_superuser or has_permission(user, "add", self.model)

    def has_table_wide_view_permission(self, user: AbstractUser) -> bool:
        return user.is_superuser or has_permission(user, "view", self.model)

    def has_table_wide_change_permission(self, user: AbstractUser) -> bool:
        return user.is_superuser or has_permission(user, "change", self.model)

    def has_table_wide_delete_permission(self, user: AbstractUser) -> bool:
        return user.is_superuser or has_permission(user, "delete", self.model)

    # Row permissions

    def rows_with_view_permission(self, user: AbstractUser) -> QuerySet:
        return (self if self.has_table_wide_view_permission(user) else self.none()) \
               | self.rows_with_extra_view_permission(user)

    def rows_with_change_permission(self, user: AbstractUser) -> QuerySet:
        return (self if self.has_table_wide_change_permission(user) else self.none()) \
               | self.rows_with_extra_change_permission(user)

    def rows_with_delete_permission(self, user: AbstractUser) -> QuerySet:
        return (self if self.has_table_wide_delete_permission(user) else self.none()) \
               | self.rows_with_extra_delete_permission(user)

    def rows_with_extra_view_permission(self, user: AbstractUser) -> QuerySet:
        return self.none()

    def rows_with_extra_change_permission(self, user: AbstractUser) -> QuerySet:
        return self.none()

    def rows_with_extra_delete_permission(self, user: AbstractUser) -> QuerySet:
        return self.none()

    # Column permissions
    @classmethod
    def addable_fields(cls, user: AbstractUser) -> FrozenSet[str]:
        return frozenset(all_field_names(cls.model))

    @staticmethod
    def viewable_fields(user: AbstractUser, obj) -> FrozenSet[str]:
        return frozenset(all_field_names(obj))

    @staticmethod
    def changeable_fields(user: AbstractUser, obj) -> FrozenSet[str]:
        return frozenset(all_field_names(obj))

    def has_some_permissions(self, user: AbstractUser) -> bool:
        return ((self if self.has_table_wide_add_permission(user) else self.none()) | \
                self.rows_with_delete_permission(user) | \
                self.rows_with_change_permission(user) | \
                self.rows_with_view_permission(user)).exists()

    def rows_with_some_permission(self, user: AbstractUser) -> QuerySet:
        return self.rows_with_delete_permission(user) | \
               self.rows_with_change_permission(user) | \
               self.rows_with_view_permission(user)

    def contains(self, obj: Model) -> bool:
        return self.filter(pk=obj.pk).exists()


def is_confidential(model: Model) -> bool:
    return issubclass(model.objects._queryset_class, ConfidentialQuerySet)
