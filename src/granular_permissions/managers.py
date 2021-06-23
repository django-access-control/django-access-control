from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import QuerySet


class ConfidentialQuerySet(models.QuerySet):
    def can(self, subject: AbstractUser, action: str) -> QuerySet:
        """
        Return a QuerySet with object on which the user `subject` can perform the specified `action`.
        Raise `NonexistentPermission` if the `action` is not in the scope of known actions.
        """

    def can_view(self, subject: AbstractUser) -> QuerySet:
        return self.none()

    def can_change(self, subject: AbstractUser) -> QuerySet:
        return self.none()

    def can_delete(self, subject: AbstractUser) -> QuerySet:
        return self.none()

    def has_any_permissions(self, subject: AbstractUser) -> bool:
        return (self.can_view(subject) | self.can_change(subject) | self.can_delete(subject)).exists()
