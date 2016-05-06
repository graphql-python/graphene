from graphql.type import GraphQLScalarType

from ..types.base import MountedType
from .base import ClassType


class Scalar(ClassType, MountedType):

    @classmethod
    def internal_type(cls, schema):
        serialize = getattr(cls, 'serialize')
        parse_literal = getattr(cls, 'parse_literal')
        parse_value = getattr(cls, 'parse_value')

        return GraphQLScalarType(
            name=cls._meta.type_name,
            description=cls._meta.description,
            serialize=serialize,
            parse_value=parse_value,
            parse_literal=parse_literal
        )
