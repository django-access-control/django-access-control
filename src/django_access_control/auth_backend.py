from django.apps import apps
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import AbstractUser

from .permissions import is_confidential


class AuthenticationBackend(BaseBackend):
    """
    This backend does not handle user authentication, it only handles permissions.
    """

    def has_module_perms(self, user_obj: AbstractUser, app_label: str) -> bool:
        """
        Return True if user_obj has any permissions in the given app_label.
        """
        app_models = list(apps.get_app_config(app_label).get_models())
        confidential_models = {m for m in app_models if is_confidential(m)}
        return any({m.objects.all().has_any_permissions(user_obj) for m in confidential_models})
