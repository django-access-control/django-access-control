from __future__ import annotations
from typing import TYPE_CHECKING

from django.contrib.auth.models import AbstractUser
from django.db.models import QuerySet

if TYPE_CHECKING: from .permissions import ObjectAction


class ConfidentialQuerySet(QuerySet):
    def can(self, subject: AbstractUser, action: ObjectAction) -> QuerySet:
        """
        Return a QuerySet with object on which the user `subject` can perform the specified `verb`.
        """
        if action == "add": raise ValueError("Add permission can only be given for models, not individual objects")
        cases = {
            "view": self.can_view(subject),
            "change": self.can_change(subject),
            "delete": self.can_delete(subject),
        }
        return cases[action]

    def can_view(self, user: AbstractUser) -> QuerySet:
        return self.none()

    def can_change(self, user: AbstractUser) -> QuerySet:
        return self.none()

    def can_delete(self, user: AbstractUser) -> QuerySet:
        return self.none()

    def has_any_permissions(self, subject: AbstractUser) -> bool:
        return (self.can_view(subject) | self.can_change(subject) | self.can_delete(subject)).exists()
