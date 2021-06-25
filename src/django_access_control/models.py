from typing import List, Type

from django.db.models import Model
from django.forms import fields_for_model


def all_field_names(model: Type[Model]) -> List[str]:
    return list(fields_for_model(model).keys())
