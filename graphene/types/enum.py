from collections import OrderedDict

import six

from ..generators import generate_enum
from ..utils.is_base_type import is_base_type
from .options import Options
from .unmountedtype import UnmountedType

try:
    from enum import Enum as PyEnum
except ImportError:
    from ..utils.enum import Enum as PyEnum


class EnumTypeMeta(type):

    def __new__(cls, name, bases, attrs):
        # Also ensure initialization is only performed for subclasses of Model
        # (excluding Model class itself).
        if not is_base_type(bases, EnumTypeMeta):
            return type.__new__(cls, name, bases, attrs)

        options = Options(
            attrs.pop('Meta', None),
            name=name,
            description=attrs.get('__doc__'),
            enum=None,
        )
        if not options.enum:
            options.enum = PyEnum(cls.__name__, attrs)

        new_attrs = OrderedDict(attrs, _meta=options, **options.enum.__members__)
        return type.__new__(cls, name, bases, new_attrs)

    def __prepare__(name, bases, **kwargs):  # noqa: N805
        return OrderedDict()

    def __call__(cls, *args, **kwargs):  # noqa: N805
        if cls is Enum:
            description = kwargs.pop('description', None)
            return cls.from_enum(PyEnum(*args, **kwargs), description=description)
        return super(EnumTypeMeta, cls).__call__(*args, **kwargs)

    def from_enum(cls, enum, description=None):
        meta_class = type('Meta', (object,), {'enum': enum, 'description': description})
        return type(meta_class.enum.__name__, (Enum,), {'Meta': meta_class})

    def __str__(cls):
        return cls._meta.name


class Enum(six.with_metaclass(EnumTypeMeta, UnmountedType)):
    def get_type(self):
        return type(self)
