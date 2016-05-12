import six
from graphql.type import GraphQLList, GraphQLNonNull

from .base import LazyType, MountedType, MountType


class OfType(MountedType):

    def __init__(self, of_type, *args, **kwargs):
        if isinstance(of_type, six.string_types):
            of_type = LazyType(of_type)
        self.of_type = of_type
        super(OfType, self).__init__(*args, **kwargs)

    def internal_type(self, schema):
        return self.T(schema.T(self.of_type))

    def mount(self, cls):
        self.parent = cls
        if isinstance(self.of_type, MountType):
            self.of_type.mount(cls)


class List(OfType):
    T = GraphQLList


class NonNull(OfType):
    T = GraphQLNonNull
