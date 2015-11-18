from graphql_relay.node.node import to_global_id

from ..core.types import (Boolean, Field, InputObjectType, Interface, List,
                          Mutation, ObjectType, String)
from ..core.types.argument import ArgumentsGroup
from ..core.types.base import LazyType
from ..core.types.definitions import NonNull
from ..utils import memoize
from .fields import GlobalIDField


class PageInfo(ObjectType):
    has_next_page = Boolean(
        required=True,
        description='When paginating forwards, are there more items?')
    has_previous_page = Boolean(
        required=True,
        description='When paginating backwards, are there more items?')
    start_cursor = String(
        description='When paginating backwards, the cursor to continue.')
    end_cursor = String(
        description='When paginating forwards, the cursor to continue.')


class Edge(ObjectType):
    '''An edge in a connection.'''
    cursor = String(
        required=True, description='A cursor for use in pagination')

    @classmethod
    @memoize
    def for_node(cls, node):
        from graphene.relay.utils import is_node
        assert is_node(node), 'ObjectTypes in a edge have to be Nodes'
        node_field = Field(node, description='The item at the end of the edge')
        return type(
            '%s%s' % (node._meta.type_name, cls._meta.type_name),
            (cls,),
            {'node_type': node, 'node': node_field})


class Connection(ObjectType):
    '''A connection to a list of items.'''
    class Meta:
        type_name = 'DefaultConnection'

    page_info = Field(PageInfo, required=True,
                      description='The Information to aid in pagination')

    _connection_data = None

    @classmethod
    @memoize
    def for_node(cls, node, edge_type=None):
        from graphene.relay.utils import is_node
        edge_type = edge_type or Edge.for_node(node)
        assert is_node(node), 'ObjectTypes in a connection have to be Nodes'
        edges = List(edge_type, description='Information to aid in pagination.')
        return type(
            '%s%s' % (node._meta.type_name, cls._meta.type_name),
            (cls,),
            {'edge_type': edge_type, 'edges': edges})

    def set_connection_data(self, data):
        self._connection_data = data

    def get_connection_data(self):
        return self._connection_data


class BaseNode(object):

    @classmethod
    def _prepare_class(cls):
        from graphene.relay.utils import is_node
        if is_node(cls):
            assert hasattr(
                cls, 'get_node'), 'get_node classmethod not found in %s Node' % cls

    def to_global_id(self):
        type_name = self._meta.type_name
        return to_global_id(type_name, self.id)

    connection_type = Connection
    edge_type = Edge

    @classmethod
    def get_connection_type(cls):
        return cls.connection_type

    @classmethod
    def get_edge_type(cls):
        return cls.edge_type


class Node(BaseNode, Interface):
    '''An object with an ID'''
    id = GlobalIDField()


class MutationInputType(InputObjectType):
    client_mutation_id = String(required=True)


class ClientIDMutation(Mutation):
    client_mutation_id = String(required=True)

    @classmethod
    def _construct_arguments(cls, items):
        assert hasattr(
            cls, 'mutate_and_get_payload'), 'You have to implement mutate_and_get_payload'
        new_input_type = type('{}Input'.format(
            cls._meta.type_name), (MutationInputType, ), items)
        cls.add_to_class('input_type', new_input_type)
        return ArgumentsGroup(input=NonNull(new_input_type))

    @classmethod
    def mutate(cls, instance, args, info):
        input = args.get('input')
        payload = cls.mutate_and_get_payload(input, info)
        client_mutation_id = input.get('client_mutation_id')
        setattr(payload, 'client_mutation_id', client_mutation_id)
        return payload
