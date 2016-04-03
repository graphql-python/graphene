import six
from graphql.core.type import GraphQLEnumType, GraphQLEnumValue

from ...utils.enum import Enum as PyEnum
from .base import ClassType, ClassTypeMeta


class EnumMeta(ClassTypeMeta):

    def construct(cls, bases, attrs):
        __enum__ = attrs.get('__enum__', None)
        if not cls._meta.abstract and not __enum__:
            __enum__ = PyEnum(cls._meta.type_name, attrs)
            setattr(cls, '__enum__', __enum__)
        if __enum__:
            for k, v in __enum__.__members__.items():
                attrs[k] = v.value
        return super(EnumMeta, cls).construct(bases, attrs)

    def __call__(cls, name, names=None, description=None):
        attrs = {
            '__enum__': PyEnum(name, names)
        }
        if description:
            attrs['__doc__'] = description
        return type(name, (Enum,), attrs)


class Enum(six.with_metaclass(EnumMeta, ClassType)):

    class Meta:
        abstract = True

    @classmethod
    def internal_type(cls, schema):
        if cls._meta.abstract:
            raise Exception("Abstract Enum don't have a specific type.")

        values = {k: GraphQLEnumValue(v.value) for k, v in cls.__enum__.__members__.items()}
        # GraphQLEnumValue
        return GraphQLEnumType(
            cls._meta.type_name,
            values=values,
            description=cls._meta.description,
        )
