from collections import OrderedDict

from ..types.field import Field, InputField
from ..types.unmountedtype import UnmountedType
from .get_graphql_type import get_graphql_type
from .is_graphene_type import is_graphene_type


def get_fields_from_attrs(in_type, attrs):
    for attname, value in list(attrs.items()):
        is_field = isinstance(value, (Field, InputField))
        is_field_proxy = isinstance(value, UnmountedType)
        if not (is_field or is_field_proxy):
            continue
        field = value.as_mounted(in_type) if is_field_proxy else value
        yield attname, field


def get_fields_from_bases_and_types(bases, types):
    fields = set()
    for _class in bases:
        if not is_graphene_type(_class):
            continue
        _fields = get_graphql_type(_class)._fields
        if callable(_fields):
            _fields = _fields()

        for default_attname, field in _fields.items():
            attname = getattr(field, 'attname', default_attname)
            if attname in fields:
                continue
            fields.add(attname)
            yield attname, field

    for grapqhl_type in types:
        for attname, field in get_graphql_type(grapqhl_type).get_fields().items():
            if attname in fields:
                continue
            fields.add(attname)
            yield attname, field


def get_fields(in_type, attrs, bases, graphql_types=()):
    fields = []

    extended_fields = list(get_fields_from_bases_and_types(bases, graphql_types))
    local_fields = list(get_fields_from_attrs(in_type, attrs))
    # We asume the extended fields are already sorted, so we only
    # have to sort the local fields, that are get from attrs
    # and could be unordered as is a dict and not OrderedDict
    local_fields = sorted(local_fields, key=lambda kv: kv[1])

    field_names = set(f[0] for f in local_fields)
    for name, extended_field in extended_fields:
        if name in field_names:
            continue
        fields.append((name, extended_field))
        field_names.add(name)

    fields.extend(local_fields)

    return OrderedDict(fields)
