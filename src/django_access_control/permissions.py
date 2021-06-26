from typing import Literal, Type

from django.contrib.auth.models import AbstractUser
from django.db.models import Model

ModelAction = Literal["add", "view", "change", "delete"]


def has_permission(user: AbstractUser, action: ModelAction, model: Type[Model]) -> bool:
    permission_str = f"{model._meta.app_label}.{action}_{model._meta.model_name}"
    return user.has_perm(permission_str)
