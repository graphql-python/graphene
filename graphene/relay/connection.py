from collections import Iterable

from graphql_relay.connection.arrayconnection import connection_from_list

from ..core.classtypes import ObjectType
from ..core.types import Field, Boolean, String, List
from ..utils import memoize


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
        edge_type = edge_type or Edge.for_node(node)
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
