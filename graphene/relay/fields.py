import collections

from graphql_relay.connection.arrayconnection import (
    connectionFromArray
)
from graphql_relay.connection.connection import (
    connectionArgs
)
from graphql_relay.node.node import (
    globalIdField
)

from graphene.core.fields import Field, LazyNativeField
from graphene.utils import cached_property
from graphene.utils import memoize


class ConnectionField(Field):
    def __init__(self, field_type, resolve=None, description=''):
        super(ConnectionField, self).__init__(field_type, resolve=resolve, 
                                              args=connectionArgs, description=description)

    def wrap_resolved(self, value, instance, args, info):
        return value

    def resolve(self, instance, args, info):
        resolved = super(ConnectionField, self).resolve(instance, args, info)
        if resolved:
            resolved = self.wrap_resolved(resolved, instance, args, info)
            assert isinstance(resolved, collections.Iterable), 'Resolved value from the connection field have to be iterable'
            return connectionFromArray(resolved, args)

    @memoize
    def internal_type(self, schema):
        from graphene.relay.types import BaseNode
        object_type = self.get_object_type(schema)
        assert issubclass(object_type, BaseNode), 'Only nodes have connections.'
        return object_type.get_connection(schema)


class NodeField(LazyNativeField):
    def get_field(self, schema):
        from graphene.relay.types import BaseNode
        return BaseNode.get_definitions(schema).nodeField


class NodeIDField(LazyNativeField):
    def get_field(self, schema):
        return globalIdField(self.object_type._meta.type_name)
