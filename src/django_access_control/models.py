from typing import Type, Set, List

from django.db.models import Model
from django.forms import fields_for_model


def all_field_names(model: Type[Model]) -> List[str]:
    return fields_for_model(model).keys()
