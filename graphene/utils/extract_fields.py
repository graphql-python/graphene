import copy
from .get_graphql_type import get_graphql_type

from ..types.field import Field, InputField
from ..types.unmountedtype import UnmountedType


def extract_fields(cls, attrs):
    fields = set()
    _fields = list()
    for attname, value in list(attrs.items()):
        is_field = isinstance(value, (Field, InputField))
        is_field_proxy = isinstance(value, UnmountedType)
        if not (is_field or is_field_proxy):
            continue
        field = value.as_mounted(cls) if is_field_proxy else copy.copy(value)
        field.attname = attname
        field.parent = cls
        fields.add(attname)
        del attrs[attname]
        _fields.append(field)

    # All the fields are Graphene Fields or InputFields, so
    # are orderable
    return sorted(_fields)


def get_base_fields(cls, bases):
    fields = set()
    _fields = list()
    for _class in bases:
        for attname, field in get_graphql_type(_class).get_fields().items():
            if attname in fields:
                continue
            field = copy.copy(field)
            if isinstance(field, (Field, InputField)):
                field.parent = cls
            fields.add(attname)
            _fields.append(field)

    return _fields
