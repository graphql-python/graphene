
from ...types import AbstractType, Field, List, NonNull, ObjectType, String
from ..connection import Connection, PageInfo
from ..node import Node


class MyObject(ObjectType):

    class Meta:
        interfaces = [Node]
    field = String()


def test_connection():
    class MyObjectConnection(Connection):
        extra = String()

        class Meta:
            node = MyObject

        class Edge:
            other = String()

    assert MyObjectConnection._meta.name == 'MyObjectConnection'
    fields = MyObjectConnection._meta.fields
    assert list(fields.keys()) == ['page_info', 'edges', 'extra']
    edge_field = fields['edges']
    pageinfo_field = fields['page_info']

    assert isinstance(edge_field, Field)
    assert isinstance(edge_field.type, List)
    assert edge_field.type.of_type == MyObjectConnection.Edge

    assert isinstance(pageinfo_field, Field)
    assert isinstance(pageinfo_field.type, NonNull)
    assert pageinfo_field.type.of_type == PageInfo


def test_connection_inherit_abstracttype():
    class BaseConnection(AbstractType):
        extra = String()

    class MyObjectConnection(BaseConnection, Connection):

        class Meta:
            node = MyObject

    assert MyObjectConnection._meta.name == 'MyObjectConnection'
    fields = MyObjectConnection._meta.fields
    assert list(fields.keys()) == ['page_info', 'edges', 'extra']


def test_edge():
    class MyObjectConnection(Connection):

        class Meta:
            node = MyObject

        class Edge:
            other = String()

    Edge = MyObjectConnection.Edge
    assert Edge._meta.name == 'MyObjectEdge'
    edge_fields = Edge._meta.fields
    assert list(edge_fields.keys()) == ['node', 'cursor', 'other']

    assert isinstance(edge_fields['node'], Field)
    assert edge_fields['node'].type == MyObject

    assert isinstance(edge_fields['other'], Field)
    assert edge_fields['other'].type == String


def test_edge_with_bases():
    class BaseEdge(AbstractType):
        extra = String()

    class MyObjectConnection(Connection):

        class Meta:
            node = MyObject

        class Edge(BaseEdge):
            other = String()

    Edge = MyObjectConnection.Edge
    assert Edge._meta.name == 'MyObjectEdge'
    edge_fields = Edge._meta.fields
    assert list(edge_fields.keys()) == ['node', 'cursor', 'extra', 'other']

    assert isinstance(edge_fields['node'], Field)
    assert edge_fields['node'].type == MyObject

    assert isinstance(edge_fields['other'], Field)
    assert edge_fields['other'].type == String


def test_edge_on_node():
    Edge = MyObject.Connection.Edge
    assert Edge._meta.name == 'MyObjectEdge'
    edge_fields = Edge._meta.fields
    assert list(edge_fields.keys()) == ['node', 'cursor']

    assert isinstance(edge_fields['node'], Field)
    assert edge_fields['node'].type == MyObject


def test_pageinfo():
    assert PageInfo._meta.name == 'PageInfo'
    fields = PageInfo._meta.fields
    assert list(fields.keys()) == ['has_next_page', 'has_previous_page', 'start_cursor', 'end_cursor']
