from collections import OrderedDict

from .dynamic import Dynamic
from .field import Field
from .inputfield import InputField
from .unmountedtype import UnmountedType


def merge(*dicts):
    merged = OrderedDict()
    for _dict in dicts:
        merged.update(_dict)
    return merged


def get_base_fields(bases, _as=None):
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


def mount_as(unmounted_field, _as):
    '''
    Mount the UnmountedType dinamically as Field or InputField
    '''
    if _as is None:
        return unmounted_field

    elif _as is Field:
        return unmounted_field.Field()

    elif _as is InputField:
        return unmounted_field.InputField()

    raise Exception(
        'Unmounted field "{}" cannot be mounted in {}.'.format(
            unmounted_field, _as
        )
    )


def get_field_as(value, _as=None):
    if isinstance(value, (Field, InputField, Dynamic)):
        return value
    elif isinstance(value, UnmountedType):
        return mount_as(value, _as)


def yank_fields_from_attrs(attrs, _as=None):
    fields_with_names = []
    for attname, value in list(attrs.items()):
        field = get_field_as(value, _as)
        if not field:
            continue
        fields_with_names.append((attname, field))
        del attrs[attname]

    return OrderedDict(sorted(fields_with_names, key=lambda f: f[1]))
