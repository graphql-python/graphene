import inspect
from collections import OrderedDict
from functools import partial
from six import string_types

from ..utils.module_loading import import_string
from .mountedtype import MountedType
from .unmountedtype import UnmountedType


def merge(*dicts):
    '''
    Merge the dicts into one
    '''
    merged = OrderedDict()
    for _dict in dicts:
        merged.update(_dict)
    return merged


def get_base_fields(bases, _as=None):
    '''
    Get all the fields in the given bases
    '''
    fields = OrderedDict()
    from ..types import AbstractType, Interface
    # We allow inheritance in AbstractTypes and Interfaces but not ObjectTypes
    inherited_bases = (AbstractType, Interface)
    for base in bases:
        if base in inherited_bases or not issubclass(base, inherited_bases):
            continue
        for name, field in base._meta.fields.items():
            if name in fields:
                continue
            fields[name] = get_field_as(field, _as=_as)

    return fields


def get_field_as(value, _as=None):
    '''
    Get type mounted
    '''
    if isinstance(value, MountedType):
        return value
    elif isinstance(value, UnmountedType):
        if _as is None:
            return value
        return _as.mounted(value)


def yank_fields_from_attrs(attrs, _as=None, delete=True, sort=True):
    '''
    Extract all the fields in given attributes (dict)
    and return them ordered
    '''
    fields_with_names = []
    for attname, value in list(attrs.items()):
        field = get_field_as(value, _as)
        if not field:
            continue
        fields_with_names.append((attname, field))
        if delete:
            del attrs[attname]

    if sort:
        fields_with_names = sorted(fields_with_names, key=lambda f: f[1])
    return OrderedDict(fields_with_names)


def get_type(_type):
    if isinstance(_type, string_types):
        return import_string(_type)
    if inspect.isfunction(_type) or type(_type) is partial:
        return _type()
    return _type
