from graphql.core.type import (GraphQLBoolean, GraphQLFloat, GraphQLID,
                               GraphQLInt, GraphQLString)

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
