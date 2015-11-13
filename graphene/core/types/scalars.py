from graphql.core.type import (GraphQLBoolean, GraphQLFloat, GraphQLID,
                               GraphQLInt, GraphQLScalarType, GraphQLString)

from .base import MountedType


class String(MountedType):
    T = GraphQLString


class Int(MountedType):
    T = GraphQLInt


class Boolean(MountedType):
    T = GraphQLBoolean


class ID(MountedType):
    T = GraphQLID


class Float(MountedType):
    T = GraphQLFloat


class Scalar(MountedType):

    @classmethod
    def internal_type(cls, schema):
        serialize = getattr(cls, 'serialize')
        parse_literal = getattr(cls, 'parse_literal')
        parse_value = getattr(cls, 'parse_value')

        return GraphQLScalarType(
            name=cls.__name__,
            description=cls.__doc__,
            serialize=serialize,
            parse_value=parse_value,
            parse_literal=parse_literal
        )
