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
        super_new = type.__new__

        # Also ensure initialization is only performed for subclasses of Model
        # (excluding Model class itself).
        if not is_base_type(bases, EnumTypeMeta):
            return super_new(cls, name, bases, attrs)

        options = Options(
            attrs.pop('Meta', None),
            name=None,
            description=None,
            enum=None,
            graphql_type=None
        )
        if not options.enum:
            options.enum = PyEnum(cls.__name__, attrs)

        new_attrs = OrderedDict(attrs, _meta=options, **options.enum.__members__)

        cls = super_new(cls, name, bases, new_attrs)

        if not options.graphql_type:
            options.graphql_type = generate_enum(cls)

        return cls

    def __prepare__(name, bases, **kwargs):  # noqa: N805
        return OrderedDict()

    def __call__(cls, *args, **kwargs):  # noqa: N805
        if cls is Enum:
            description = kwargs.pop('description', None)
            return cls.from_enum(PyEnum(*args, **kwargs), description=description)
        return super(EnumTypeMeta, cls).__call__(*args, **kwargs)


class Enum(six.with_metaclass(EnumTypeMeta, UnmountedType)):

    @classmethod
    def from_enum(cls, enum, description=None):
        meta_class = type('Meta', (object,), {'enum': enum, 'description': description})
        return type(meta_class.enum.__name__, (Enum,), {'Meta': meta_class})
