from ..types.field import Field
from ..types.unmountedtype import UnmountedType


def as_field(value):
    if isinstance(value, UnmountedType):
        return value.as_field()
    elif isinstance(value, Field):
        return value
    raise Exception("{} is not a field".format(value))
