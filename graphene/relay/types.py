from graphql_relay.node.node import (
    to_global_id
)
from graphql_relay.connection.connection import (
    connection_definitions
)

from graphene.core.types import Interface, ObjectType
from graphene.core.fields import BooleanField, StringField, ListField, Field
from graphene.relay.fields import GlobalIDField
from graphene.utils import memoize


class BaseNode(object):
    @classmethod
    @memoize
    def get_connection(cls, schema):
        _type = cls.internal_type(schema)
        type_name = cls._meta.type_name
        connection = connection_definitions(type_name, _type).connection_type
        return connection

    @classmethod
    def _prepare_class(cls):
        from graphene.relay.utils import is_node
        if is_node(cls):
            assert hasattr(
                cls, 'get_node'), 'get_node classmethod not found in %s Node' % cls

    @classmethod
    def to_global_id(cls, instance, args, info):
        type_name = cls._meta.type_name
        return to_global_id(type_name, instance.id)


class Node(BaseNode, Interface):
    '''An object with an ID'''
    id = GlobalIDField()


class PageInfo(ObjectType):
    has_next_page = BooleanField(required=True, description='When paginating forwards, are there more items?')
    has_previous_page = BooleanField(required=True, description='When paginating backwards, are there more items?')
    start_cursor = StringField(description='When paginating backwards, the cursor to continue.')
    end_cursor = StringField(description='When paginating forwards, the cursor to continue.')


class Edge(ObjectType):
    '''An edge in a connection.'''
    node = Field(lambda field: field.object_type.node_type, description='The item at the end of the edge')
    end_cursor = StringField(required=True, description='A cursor for use in pagination')

    @classmethod
    @memoize
    def for_node(cls, node):
        from graphene.relay.utils import is_node
        assert is_node(node), 'ObjectTypes in a edge have to be Nodes'
        return type('%sEdge' % node._meta.type_name, (cls, ), {'node_type': node})


class Connection(ObjectType):
    '''A connection to a list of items.'''
    page_info = Field(PageInfo, required=True, description='The Information to aid in pagination')
    edges = ListField(lambda field: field.object_type.edge_type, description='Information to aid in pagination.')

    @classmethod
    @memoize
    def for_node(cls, node, edge_type=None):
        from graphene.relay.utils import is_node
        edge_type = edge_type or Edge
        assert is_node(node), 'ObjectTypes in a connection have to be Nodes'
        return type('%sConnection' % node._meta.type_name, (cls, ), {'edge_type': edge_type.for_node(node)})
