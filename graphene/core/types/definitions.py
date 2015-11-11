import six
from graphql.core.type import (GraphQLList, GraphQLNonNull)

from .base import MountedType, LazyType


class OfType(MountedType):
    def __init__(self, of_type, *args, **kwargs):
        if isinstance(of_type, six.string_types) and of_type != 'self':
            of_type = LazyType(of_type)
        self.of_type = of_type
        super(OfType, self).__init__(*args, **kwargs)

    def internal_type(self, schema):
        return self.T(schema.T(self.of_type))


class List(OfType):
    T = GraphQLList


class NonNull(OfType):
    T = GraphQLNonNull
