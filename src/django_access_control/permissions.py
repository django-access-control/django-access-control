from typing import Literal, Any

from django.contrib.auth.models import AbstractUser
from django.db.models import Model

from .managers import ConfidentialQuerySet

ModelAction = Literal["add", "view", "change", "delete"]
ObjectAction = Literal["view", "change", "delete"]
FieldAction = Literal["view", "change"]


class Permission:

    def is_authorized(self, user: AbstractUser) -> bool:
        return user.is_superuser


class AllModelPermission(Permission):

    def __init__(self, action: ModelAction, model: Model):
        self.action = action
        self.model = model

    def is_authorized(self, user: AbstractUser) -> bool:
        return super().is_authorized(user) or has_model_permission(user, self.action, self.model)


class AnyModelPermission(AllModelPermission):

    def is_authorized(self, user: AbstractUser) -> bool:
        return super().is_authorized(user) or (
                is_confidential(self.model) and self.model.objects.all().can(user, self.action).exists())


class AllObjectPermission(AllModelPermission):

    def __init__(self, action: ModelAction, model: Model, pk: Any):
        super().__init__(action, model)
        self.pk = pk

    def is_authorized(self, user: AbstractUser) -> bool:
        return super().is_authorized(user) or (
                is_confidential(self.model) and self.model.objects.all().can(user, self.action).filter(
            pk=self.pk).exists())


def has_model_permission(user: AbstractUser, action: ModelAction, model: Model) -> bool:
    permission_str = f"{model._meta.app_label}.{action}_{model._meta.model_name}"
    return user.has_perm(permission_str)


def is_confidential(model: Model) -> bool:
    return issubclass(model.objects._queryset_class, ConfidentialQuerySet)

#
# @dataclass(frozen=True)
# class Permission:
#     quantifier: Quantifier
#     verb: Verb
#     app_label: str
#     model_name: str
#     pk: Optional[str]
#     field: Optional[str]
#
#     def __post_init__(self):
#         MalformedPermission.ensure(self.app_label is not None, "App label cannot be None")
#         MalformedPermission.ensure(self.model_name is not None, "Model name cannot be None")
#         if self.app_label not in {a.name for a in apps.get_app_configs()}:
#             raise MalformedPermission(f"Application with name `{self.app_label}` is not installed")
#         if self.model_name not in {m.__name__ for m in apps.get_app_config(self.app_label).get_models()}:
#             raise MalformedPermission(f"Application {self.app_label} has no model named {self.model_name}")
#         MalformedPermission.preclude(self.pk is None and self.field is not None, "`field` cannot be given without `pk`")
#         if self.verb == "add":
#             MalformedPermission.ensure(self.pk is None and self.field is None,
#                                        "Add permission can be granted to a model, not to a single object or its field")
#         if self.verb == "delete":
#             MalformedPermission.ensure(self.field is None,
#                                        "Delete permission can be granted to a model or object, not to a single field")
#
#     def __repr__(self) -> str:
#         """
#         E.g. A/view/users.User.1.name
#         """
#         noun = '.'.join([n for n in (self.app_label, self.model_name, self.pk, self.field) if n is not None])
#         return f"{self.quantifier}/{self.verb}/{noun}"
#
#     @property
#     def scope(self) -> PermissionScope:
#         if self.pk is None: return PermissionScope.MODEL
#         if self.field is None: return PermissionScope.FIELD
#         return PermissionScope.FIELD
#
#     @property
#     def model(self) -> Model:
#         app_models = list(apps.get_app_config(self.app_label).get_models())
#         for m in app_models:
#             if m.__name__ == self.model_name: return m
#
#
# def permission(code: str) -> Permission:
#     quantifier, verb, noun = code.split("/")
#     app, model, pk, field, *_ = noun.split(".") + [None, None, None, None]
#     return Permission(Quantifier(quantifier), Verb(verb), app, model, pk, field)
