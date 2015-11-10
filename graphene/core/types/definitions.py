from graphql.core.type import (GraphQLList, GraphQLNonNull)

from .base import MountedType


class OfType(MountedType):
    def __init__(self, of_type, *args, **kwargs):
        self.of_type = of_type
        super(OfType, self).__init__(*args, **kwargs)

    def internal_type(self, schema):
        return self.T(schema.T(self.of_type))


class List(OfType):
    T = GraphQLList


class NonNull(OfType):
    T = GraphQLNonNull
