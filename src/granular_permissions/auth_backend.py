from django.apps import apps
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import AbstractUser

from granular_permissions.managers import ConfidentialQuerySet


class AuthenticationBackend(BaseBackend):
    """
    This backend does not handle user authentication, it only handles permissions.
    """

    # def get_user_permissions(self, user_obj, obj=None):
    #     """
    #     Return a set of permission strings the user `user_obj` has from their
    #     `user_permissions`.
    #     """
    #     return self._get_permissions(user_obj, obj, 'user')
    #
    # def get_group_permissions(self, user_obj, obj=None):
    #     """
    #     Return a set of permission strings the user `user_obj` has from the
    #     groups they belong.
    #     """
    #     return self._get_permissions(user_obj, obj, 'group')
    #
    # def get_all_permissions(self, user_obj, obj=None):
    #     if not user_obj.is_active or user_obj.is_anonymous or obj is not None:
    #         return set()
    #     if not hasattr(user_obj, '_perm_cache'):
    #         user_obj._perm_cache = super().get_all_permissions(user_obj)
    #     return user_obj._perm_cache

    # def has_perm(self, user_obj, perm, obj=None):
    #     return user_obj.is_active and super().has_perm(user_obj, perm, obj=obj)

    def has_module_perms(self, user_obj: AbstractUser, app_label: str) -> bool:
        """
        Return True if user_obj has any permissions in the given app_label.
        """
        app_models = list(apps.get_app_config(app_label).get_models())
        confidential_models = {m for m in app_models if m.objects.__class__.__name__ == 'ManagerFromUserQueryset'}
        print(user_obj, 'has permissions for', app_label,
              any({m.objects.has_any_permissions(user_obj) for m in confidential_models}))
        return any({m.objects.has_any_permissions(user_obj) for m in confidential_models})
