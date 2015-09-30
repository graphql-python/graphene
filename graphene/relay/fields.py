import collections

from graphql_relay.connection.arrayconnection import (
    connectionFromArray
)
from graphql_relay.connection.connection import (
    connectionArgs
)
from graphene.core.fields import Field, LazyNativeField
from graphene.utils import cached_property


class ConnectionField(Field):
    def __init__(self, field_type, resolve=None, description=''):
        super(ConnectionField, self).__init__(field_type, resolve=resolve, 
                                              args=connectionArgs, description=description)

    def wrap_resolved(self, value, instance, args, info):
        return value

    def resolve(self, instance, args, info):
        resolved = super(ConnectionField, self).resolve(instance, args, info)
        if resolved:
            assert isinstance(resolved, collections.Iterable), 'Resolved value from the connection field have to be iterable'
            resolved = self.wrap_resolved(resolved, instance, args, info)
            return connectionFromArray(resolved, args)

    @cached_property
    def type(self):
        object_type = self.get_object_type()
        assert issubclass(object_type, self.schema.Node), 'Only nodes have connections.'
        return object_type.connection


class NodeField(LazyNativeField):
    def get_field(self):
        return self.schema.Node._definitions.nodeField
