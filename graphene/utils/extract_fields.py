import copy
from .get_graphql_type import get_graphql_type

from ..types.field import Field
from ..types.proxy import TypeProxy


def extract_fields(attrs):
    fields = set()
    _fields = list()
    for attname, value in list(attrs.items()):
        is_field = isinstance(value, Field)
        is_field_proxy = isinstance(value, TypeProxy)
        if not (is_field or is_field_proxy):
            continue

        field = value.as_field() if is_field_proxy else copy.copy(value)
        field.attname = attname
        fields.add(attname)
        del attrs[attname]
        _fields.append(field)

    return sorted(_fields)


def get_base_fields(bases):
    fields = set()
    for _class in bases:
        for attname, field in get_graphql_type(_class).get_fields().items():
            if attname in fields:
                continue
            field = copy.copy(field)
            field.name = attname
            fields.add(attname)
            yield field
