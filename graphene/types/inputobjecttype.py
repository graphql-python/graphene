import six

from ..utils.is_base_type import is_base_type
from .abstracttype import AbstractTypeMeta
from .options import Options
from .unmountedtype import UnmountedType
from .utils import (get_fields_in_type, yank_fields_from_attrs,
                    get_base_fields, merge)


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
            local_fields=None,
        )

        options.base_fields = get_base_fields(InputObjectType, bases)

        if not options.local_fields:
            options.local_fields = get_fields_in_type(InputObjectType, attrs)
            yank_fields_from_attrs(attrs, options.local_fields)

        options.fields = merge(
            options.base_fields,
            options.local_fields
        )
        return type.__new__(cls, name, bases, dict(attrs, _meta=options))

    def __str__(cls):  # noqa: N802
        return cls._meta.name


class InputObjectType(six.with_metaclass(InputObjectTypeMeta, UnmountedType)):

    @classmethod
    def get_type(cls):
        return cls
