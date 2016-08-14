from collections import OrderedDict

from .unmountedtype import UnmountedType
from .field import Field
from .inputfield import InputField


def merge_fields_in_attrs(bases, attrs):
    from ..types import AbstractType, Interface
    inherited_bases = (AbstractType, Interface)
    for base in bases:
        if base in inherited_bases or not issubclass(base, inherited_bases):
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
    from ..types.objecttype import ObjectType
    from ..types.interface import Interface
    from ..types.abstracttype import AbstractType
    from ..types.inputobjecttype import InputObjectType

    if issubclass(type, (ObjectType, Interface)):
        return unmounted_field.Field()

    elif issubclass(type, (AbstractType)):
        return unmounted_field
    elif issubclass(type, (InputObjectType)):
        return unmounted_field.InputField()

    raise Exception(
        'Unmounted field "{}" cannot be mounted in {}.{}.'.format(
            unmounted_field, type, attname
        )
    )


def get_fields_in_type(in_type, attrs):
    fields_with_names = []
    for attname, value in list(attrs.items()):
        if isinstance(value, (Field, InputField)):
            fields_with_names.append(
                (attname, value)
            )
        elif isinstance(value, UnmountedType):
            try:
                value = unmounted_field_in_type(attname, value, in_type)
                fields_with_names.append(
                    (attname, value)
                )
            except Exception as e:
                raise Exception('Exception while mounting the field "{}": {}'.format(attname, str(e)))

    return OrderedDict(sorted(fields_with_names, key=lambda f: f[1]))


def yank_fields_from_attrs(attrs, fields):
    for name in fields.keys():
        del attrs[name]
