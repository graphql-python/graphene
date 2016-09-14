from ...types import Field, List, NonNull, ObjectType, String, AbstractType
from ..connection import Connection, PageInfo
from ..node import Node


class MyObject(ObjectType):

    class Meta:
        interfaces = [Node]
    field = String()


def xtest_connection():
    class MyObjectConnection(Connection):
        extra = String()

        class Meta:
            node = MyObject

        class Edge:
            other = String()

    assert MyObjectConnection._meta.name == 'MyObjectConnection'
    fields = MyObjectConnection._meta.fields
    assert list(fields.keys()) == ['extra', 'page_info', 'edges']
    edge_field = fields['edges']
    pageinfo_field = fields['page_info']

    assert isinstance(edge_field, Field)
    assert isinstance(edge_field.type, List)
    assert edge_field.type.of_type == MyObjectConnection.Edge

    assert isinstance(pageinfo_field, Field)
    assert isinstance(pageinfo_field.type, NonNull)
    assert pageinfo_field.type.of_type == PageInfo


def xtest_connection_inherit_abstracttype():
    class BaseConnection(AbstractType):
        extra = String()

    class MyObjectConnection(BaseConnection, Connection):
        class Meta:
            node = MyObject

    assert MyObjectConnection._meta.name == 'MyObjectConnection'
    fields = MyObjectConnection._meta.fields
    assert list(fields.keys()) == ['extra', 'page_info', 'edges']


def xtest_defaul_connection_for_type():
    MyObjectConnection = Connection.for_type(MyObject)
    assert MyObjectConnection._meta.name == 'MyObjectConnection'
    fields = MyObjectConnection._meta.fields
    assert list(fields.keys()) == ['page_info', 'edges']


def xtest_defaul_connection_for_type_returns_same_Connection():
    assert Connection.for_type(MyObject) == Connection.for_type(MyObject)

def xtest_edge():
    class MyObjectConnection(Connection):
        class Meta:
            node = MyObject

        class Edge:
            other = String()

    Edge = MyObjectConnection.Edge
    assert Edge._meta.name == 'MyObjectEdge'
    edge_fields = Edge._meta.fields
    assert list(edge_fields.keys()) == ['cursor', 'other', 'node']

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
    assert list(edge_fields.keys()) == ['extra', 'other', 'cursor', 'node']

    assert isinstance(edge_fields['node'], Field)
    assert edge_fields['node'].type == MyObject

    assert isinstance(edge_fields['other'], Field)
    assert edge_fields['other'].type == String


def xtest_pageinfo():
    assert PageInfo._meta.name == 'PageInfo'
    fields = PageInfo._meta.fields
    assert list(fields.keys()) == ['has_next_page', 'has_previous_page', 'start_cursor', 'end_cursor']


def xtest_edge_for_node_type():
    edge = Connection.for_type(MyObject).Edge

    assert edge._meta.name == 'MyObjectEdge'
    edge_fields = edge._meta.fields
    assert list(edge_fields.keys()) == ['cursor', 'node']

    assert isinstance(edge_fields['node'], Field)
    assert edge_fields['node'].type == MyObject


def xtest_edge_for_object_type():
    class MyObject(ObjectType):
        field = String()

    edge = Connection.for_type(MyObject).Edge

    assert edge._meta.name == 'MyObjectEdge'
    edge_fields = edge._meta.fields
    assert list(edge_fields.keys()) == ['cursor', 'node']

    assert isinstance(edge_fields['node'], Field)
    assert edge_fields['node'].type == MyObject


def xtest_edge_for_type_returns_same_edge():
    assert Connection.for_type(MyObject).Edge == Connection.for_type(MyObject).Edge
