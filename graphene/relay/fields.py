from collections import Iterable, OrderedDict

from graphql_relay.connection.arrayconnection import (
    connection_from_list
)
from graphql_relay.connection.connection import (
    connectionArgs
)
from graphql_relay.node.node import (
    from_global_id
)
from graphql.core.type import (
    GraphQLNonNull,
    GraphQLID,
    GraphQLArgument,
)

from graphene.core.fields import Field, IDField
from graphene.utils import memoize


class ConnectionField(Field):

    def __init__(self, field_type, resolve=None, description='', connection_type=None, edge_type=None, **kwargs):
        from graphene.relay.types import Connection, Edge
        super(ConnectionField, self).__init__(field_type, resolve=resolve,
                                              args=connectionArgs, description=description, **kwargs)
        self.connection_type = connection_type or Connection
        self.edge_type = edge_type or Edge
        assert issubclass(self.connection_type, Connection), 'connection_type in %r must be a subclass of Connection' % self
        assert issubclass(self.edge_type, Edge), 'edge_type in %r must be a subclass of Edge' % self

    def wrap_resolved(self, value, instance, args, info):
        return value

    def resolve(self, instance, args, info):
        resolved = super(ConnectionField, self).resolve(instance, args, info)
        if resolved:
            resolved = self.wrap_resolved(resolved, instance, args, info)
            assert isinstance(
                resolved, Iterable), 'Resolved value from the connection field have to be iterable'
            return connection_from_list(resolved, args)

    @memoize
    def internal_type(self, schema):
        from graphene.relay.utils import is_node
        node = self.get_object_type(schema)
        assert is_node(node), 'Only nodes have connections.'
        schema.register(node)
        edge_node_type = self.edge_type.for_node(node)
        connection_node_type = self.connection_type.for_node(node, edge_type=edge_node_type)
        return connection_node_type.internal_type(schema)


class NodeField(Field):
    def __init__(self, object_type=None, *args, **kwargs):
        from graphene.relay.types import Node
        super(NodeField, self).__init__(object_type or Node, *args, **kwargs)
        self.field_object_type = object_type
        self.args['id'] = GraphQLArgument(
            GraphQLNonNull(GraphQLID),
            description='The ID of an object'
        )

    def id_fetcher(self, global_id, info):
        from graphene.relay.utils import is_node
        schema = info.schema.graphene_schema
        resolved_global_id = from_global_id(global_id)
        _type, _id = resolved_global_id.type, resolved_global_id.id
        object_type = schema.get_type(_type)
        if not is_node(object_type) or (self.field_object_type and
           object_type != self.field_object_type):
            return

        return object_type.get_node(_id)

    def resolve(self, instance, args, info):
        global_id = args.get('id')
        return self.id_fetcher(global_id, info)


class GlobalIDField(IDField):
    '''The ID of an object'''
    required = True

    def contribute_to_class(self, cls, name, add=True):
        from graphene.relay.utils import is_node, is_node_type
        in_node = is_node(cls) or is_node_type(cls)
        assert in_node, 'GlobalIDField could only be inside a Node, but got %r' % cls
        super(GlobalIDField, self).contribute_to_class(cls, name, add)

    def resolve(self, instance, args, info):
        return self.object_type.to_global_id(instance, args, info)
