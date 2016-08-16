from collections import OrderedDict

from .dynamic import Dynamic
from .field import Field
from .inputfield import InputField
from .unmountedtype import UnmountedType


def merge_fields_in_attrs(bases, attrs):
    from ..types import AbstractType, Interface
    inherited_bases = (AbstractType, Interface)
    for base in bases:
        if base in inherited_bases or not issubclass(base, inherited_bases):
            continue
        print('!!!!!!!!!!!')
        print(base._meta)
        print(dir(base._meta))
        print(base._meta.fields.items())
        for name, field in base._meta.fields.items():
            if name in attrs:
                continue
            attrs[name] = field
    return attrs


def merge(*dicts):
    merged = OrderedDict()
    for _dict in dicts:
        merged.update(_dict)
    return merged


def get_base_fields(in_type, bases):
    fields = OrderedDict()
    fields = merge_fields_in_attrs(bases, fields)
    return get_fields_in_type(in_type, fields, order=False)


def unmounted_field_in_type(unmounted_field, type):
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
        'Unmounted field "{}" cannot be mounted in {}.'.format(
            unmounted_field, type
        )
    )


def get_field(in_type, value):
    if isinstance(value, (Field, InputField, Dynamic)):
        return value
    elif isinstance(value, UnmountedType):
        return unmounted_field_in_type(value, in_type)


def get_fields_in_type(in_type, attrs, order=True):
    fields_with_names = []
    for attname, value in list(attrs.items()):
        field = get_field(in_type, value)
        if not field:
            continue
        fields_with_names.append((attname, field))

    if not order:
        return OrderedDict(fields_with_names)

    return OrderedDict(sorted(fields_with_names, key=lambda f: f[1]))


def yank_fields_from_attrs(attrs, fields):
    for name in fields.keys():
        del attrs[name]
