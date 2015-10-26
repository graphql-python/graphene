from collections import Iterable, OrderedDict

from graphql_relay.connection.arrayconnection import (
    connection_from_list
)
from graphql_relay.connection.connection import (
    connection_args
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


class ConnectionField(Field):

    def __init__(self, field_type, resolve=None, description='',
                 connection_type=None, edge_type=None, **kwargs):
        super(ConnectionField, self).__init__(field_type, resolve=resolve,
                                              args=connection_args,
                                              description=description, **kwargs)
        self.connection_type = connection_type
        self.edge_type = edge_type

    def wrap_resolved(self, value, instance, args, info):
        return value

    def resolve(self, instance, args, info):
        from graphene.relay.types import PageInfo
        schema = info.schema.graphene_schema

        resolved = super(ConnectionField, self).resolve(instance, args, info)
        if resolved:
            resolved = self.wrap_resolved(resolved, instance, args, info)
            assert isinstance(
                resolved, Iterable), 'Resolved value from the connection field have to be iterable'

            node = self.get_object_type(schema)
            connection_type = self.get_connection_type(node)
            edge_type = self.get_edge_type(node)

            connection = connection_from_list(resolved, args, connection_type=connection_type,
                                              edge_type=edge_type, pageinfo_type=PageInfo)
            connection.set_connection_data(resolved)
            return connection

    def get_connection_type(self, node):
        connection_type = self.connection_type or node.get_connection_type()
        edge_type = self.get_edge_type(node)
        return connection_type.for_node(node, edge_type=edge_type)

    def get_edge_type(self, node):
        return self.edge_type or node.get_edge_type()

    def internal_type(self, schema):
        from graphene.relay.utils import is_node
        node = self.get_object_type(schema)
        assert is_node(node), 'Only nodes have connections.'
        schema.register(node)

        return self.get_connection_type(node).internal_type(schema)


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
