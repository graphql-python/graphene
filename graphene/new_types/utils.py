from .unmountedtype import UnmountedType
from .field import Field


def unmounted_field_in_type(attname, unmounted_field, type):
    '''
    Mount the UnmountedType dinamically as Field or InputField
    depending on where mounted in.

    ObjectType -> Field
    InputObjectType -> InputField
    '''
    # from ..types.inputobjecttype import InputObjectType
    from ..new_types.objecttype import ObjectTypeMeta
    from ..new_types.interface import Interface
    from ..new_types.abstracttype import AbstractTypeMeta

    if issubclass(type, (ObjectTypeMeta, Interface)):
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
    for attname, value in list(attrs.items()):
        if isinstance(value, (Field)):  # , InputField
            yield attname, value
        elif isinstance(value, UnmountedType):
            yield attname, unmounted_field_in_type(attname, value, in_type)


def attrs_without_fields(attrs, fields):
    return {k: v for k, v in attrs.items() if k not in fields}
