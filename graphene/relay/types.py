import inspect
import warnings
from collections import Iterable
from functools import wraps

import six

from graphql_relay.connection.arrayconnection import connection_from_list
from graphql_relay.node.node import to_global_id

from ..core.classtypes import InputObjectType, Interface, Mutation, ObjectType
from ..core.classtypes.interface import InterfaceMeta
from ..core.classtypes.mutation import MutationMeta
from ..core.types import Boolean, Field, List, String
from ..core.types.argument import ArgumentsGroup
from ..core.types.definitions import NonNull
from ..utils import memoize
from ..utils.wrap_resolver_function import has_context, with_context
from .fields import GlobalIDField


class PageInfo(ObjectType):

    def __init__(self, start_cursor="", end_cursor="",
                 has_previous_page=False, has_next_page=False, **kwargs):
        super(PageInfo, self).__init__(**kwargs)
        self.startCursor = start_cursor
        self.endCursor = end_cursor
        self.hasPreviousPage = has_previous_page
        self.hasNextPage = has_next_page

    hasNextPage = Boolean(
        required=True,
        description='When paginating forwards, are there more items?')
    hasPreviousPage = Boolean(
        required=True,
        description='When paginating backwards, are there more items?')
    startCursor = String(
        description='When paginating backwards, the cursor to continue.')
    endCursor = String(
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

    def __init__(self, edges, page_info, **kwargs):
        super(Connection, self).__init__(**kwargs)
        self.edges = edges
        self.pageInfo = page_info

    class Meta:
        type_name = 'DefaultConnection'

    pageInfo = Field(PageInfo, required=True,
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

    @classmethod
    def from_list(cls, iterable, args, context, info):
        assert isinstance(
            iterable, Iterable), 'Resolved value from the connection field have to be iterable'
        connection = connection_from_list(
            iterable, args, connection_type=cls,
            edge_type=cls.edge_type, pageinfo_type=PageInfo)
        connection.set_connection_data(iterable)
        return connection

    def set_connection_data(self, data):
        self._connection_data = data

    def get_connection_data(self):
        return self._connection_data


class NodeMeta(InterfaceMeta):

    def construct_get_node(cls):
        get_node = getattr(cls, 'get_node', None)
        assert get_node, 'get_node classmethod not found in %s Node' % cls
        assert callable(get_node), 'get_node have to be callable'
        args = 4
        if isinstance(get_node, staticmethod):
            args -= 1

        get_node_num_args = len(inspect.getargspec(get_node).args)
        if get_node_num_args < args:
            warnings.warn("get_node will receive also the info arg"
                          " in future versions of graphene".format(cls.__name__),
                          FutureWarning)

            @staticmethod
            @wraps(get_node)
            def wrapped_node(id, context=None, info=None):
                node_args = [id, info, context]
                if has_context(get_node):
                    return get_node(*node_args[:get_node_num_args - 1], context=context)
                if get_node_num_args - 1 == 0:
                    return get_node(id)
                return get_node(*node_args[:get_node_num_args - 1])
            node_func = wrapped_node
            setattr(cls, 'get_node', node_func)

    def construct(cls, *args, **kwargs):
        cls = super(NodeMeta, cls).construct(*args, **kwargs)
        if not cls._meta.abstract:
            cls.construct_get_node()
        return cls


class Node(six.with_metaclass(NodeMeta, Interface)):
    '''An object with an ID'''
    id = GlobalIDField()

    class Meta:
        abstract = True

    @classmethod
    def global_id(cls, id):
        type_name = cls._meta.type_name
        return to_global_id(type_name, id)

    def to_global_id(self):
        return self.global_id(self.id)

    connection_type = Connection
    edge_type = Edge

    @classmethod
    def get_connection_type(cls):
        return cls.connection_type

    @classmethod
    def get_edge_type(cls):
        return cls.edge_type


class MutationInputType(InputObjectType):
    clientMutationId = String(required=True)


class RelayMutationMeta(MutationMeta):

    def construct(cls, *args, **kwargs):
        cls = super(RelayMutationMeta, cls).construct(*args, **kwargs)
        if not cls._meta.abstract:
            assert hasattr(
                cls, 'mutate_and_get_payload'), 'You have to implement mutate_and_get_payload'
        return cls

    def construct_arguments(cls, items):
        new_input_type = type('{}Input'.format(
            cls._meta.type_name), (MutationInputType, ), items)
        cls.add_to_class('input_type', new_input_type)
        return ArgumentsGroup(input=NonNull(new_input_type))


class ClientIDMutation(six.with_metaclass(RelayMutationMeta, Mutation)):
    clientMutationId = String(required=True)

    class Meta:
        abstract = True

    @classmethod
    @with_context
    def mutate(cls, instance, args, context, info):
        input = args.get('input')
        if has_context(cls.mutate_and_get_payload):
            payload = cls.mutate_and_get_payload(input, context, info)
        else:
            payload = cls.mutate_and_get_payload(input, info)
        client_mutation_id = input.get('clientMutationId') or input.get('client_mutation_id')
        setattr(payload, 'clientMutationId', client_mutation_id)
        return payload
