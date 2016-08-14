import six

from ..utils.is_base_type import is_base_type
from .options import Options

from .abstracttype import AbstractTypeMeta
from .utils import get_fields_in_type, yank_fields_from_attrs, merge_fields_in_attrs
from .unmountedtype import UnmountedType


class InputObjectTypeMeta(AbstractTypeMeta):

    def __new__(cls, name, bases, attrs):
        # Also ensure initialization is only performed for subclasses of
        # InputObjectType
        if not is_base_type(bases, InputObjectTypeMeta):
            return type.__new__(cls, name, bases, attrs)

        options = Options(
            attrs.pop('Meta', None),
            name=name,
            description=attrs.get('__doc__'),
            fields=None,
        )

        attrs = merge_fields_in_attrs(bases, attrs)
        if not options.fields:
            options.fields = get_fields_in_type(InputObjectType, attrs)
            yank_fields_from_attrs(attrs, options.fields)

        return type.__new__(cls, name, bases, dict(attrs, _meta=options))

    def __str__(cls):
        return cls._meta.name


class InputObjectType(six.with_metaclass(InputObjectTypeMeta, UnmountedType)):
    @classmethod
    def get_type(cls):
        return cls
    # def __init__(self, *args, **kwargs):
    #     raise Exception("An InputObjectType cannot be intitialized")
