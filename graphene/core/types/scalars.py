from graphql.type import (GraphQLBoolean, GraphQLFloat, GraphQLID, GraphQLInt,
                          GraphQLString)

from .base import MountedType


class ScalarType(MountedType):

    def internal_type(self, schema):
        return self._internal_type


class String(ScalarType):
    _internal_type = GraphQLString


class Int(ScalarType):
    _internal_type = GraphQLInt


class Boolean(ScalarType):
    _internal_type = GraphQLBoolean


class ID(ScalarType):
    _internal_type = GraphQLID


class Float(ScalarType):
    _internal_type = GraphQLFloat
