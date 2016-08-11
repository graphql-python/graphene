from collections import OrderedDict

from .unmountedtype import UnmountedType
from .field import Field


def merge_fields_in_attrs(bases, attrs):
    from ..new_types.abstracttype import AbstractType
    for base in bases:
        if base == AbstractType or not issubclass(base, AbstractType):
            continue
        for name, field in base._meta.fields.items():
            if name in attrs:
                continue
            attrs[name] = field
    return attrs


def unmounted_field_in_type(attname, unmounted_field, type):
    '''
    Mount the UnmountedType dinamically as Field or InputField
    depending on where mounted in.

    ObjectType -> Field
    InputObjectType -> InputField
    '''
    # from ..types.inputobjecttype import InputObjectType
    from ..new_types.objecttype import ObjectTypeMeta
    from ..new_types.interface import InterfaceMeta
    from ..new_types.abstracttype import AbstractTypeMeta

    if issubclass(type, (ObjectTypeMeta, InterfaceMeta)):
        return unmounted_field.as_field()

    elif issubclass(type, (AbstractTypeMeta)):
        return unmounted_field
    # elif issubclass(type, (InputObjectType)):
    #     return unmounted_field.as_inputfield()

    raise Exception(
        'Unmounted field "{}" cannot be mounted in {}.{}.'.format(
            unmounted_field, type, attname
        )
    )


def get_fields_in_type(in_type, attrs):
    fields_with_names = []
    for attname, value in list(attrs.items()):
        if isinstance(value, (Field)):  # , InputField
            fields_with_names.append(
                (attname, value)
            )
        elif isinstance(value, UnmountedType):
            fields_with_names.append(
                (attname, unmounted_field_in_type(attname, value, in_type))
            )

    return OrderedDict(sorted(fields_with_names, key=lambda f: f[1]))


def yank_fields_from_attrs(attrs, fields):
    for name, field in fields.items():
        # attrs.pop(name, None)
        del attrs[name]
    # return attrs
    # return {k: v for k, v in attrs.items() if k not in fields}
