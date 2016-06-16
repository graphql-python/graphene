from collections import OrderedDict

import six

from graphql.type import GraphQLEnumType, GraphQLEnumValue

from ..utils.is_base_type import is_base_type
from .definitions import GrapheneGraphQLType
from .options import Options
from .unmountedtype import UnmountedType

try:
    from enum import Enum as PyEnum
except ImportError:
    from ..utils.enum import Enum as PyEnum


class GrapheneEnumType(GrapheneGraphQLType, GraphQLEnumType):
    pass


def values_from_enum(enum):
    _values = OrderedDict()
    for name, value in enum.__members__.items():
        _values[name] = GraphQLEnumValue(name=name, value=value.value)
    return _values


class EnumTypeMeta(type):

    def __new__(cls, name, bases, attrs):
        super_new = super(EnumTypeMeta, cls).__new__

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
            options.enum = type(cls.__name__, (PyEnum,), attrs)

        cls = super_new(cls, name, bases, dict(attrs, _meta=options, **options.enum.__members__))

        if not options.graphql_type:
            values = values_from_enum(options.enum)
            options.graphql_type = GrapheneEnumType(
                graphene_type=cls,
                values=values,
                name=options.name or cls.__name__,
                description=options.description or cls.__doc__,
            )

        return cls

    def __prepare__(name, bases, **kwargs):
        return OrderedDict()

    def __call__(cls, *args, **kwargs):
        if cls is Enum:
            return cls.from_enum(PyEnum(*args, **kwargs))
        return super(EnumTypeMeta, cls).__call__(*args, **kwargs)


class Enum(six.with_metaclass(EnumTypeMeta, UnmountedType)):

    @classmethod
    def from_enum(cls, python_enum):
        class Meta:
            enum = python_enum
        return type(Meta.enum.__name__, (Enum,), {'Meta': Meta})
