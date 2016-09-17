from ...types import Field, List, NonNull, ObjectType, String, AbstractType
from ..connection import Connection, PageInfo, Edge
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
    assert list(fields.keys()) == ['extra', 'edges', 'page_info']
    edge_field = fields['edges']
    pageinfo_field = fields['page_info']

    assert isinstance(edge_field, Field)
    assert isinstance(edge_field.type, List)
    assert edge_field.type.of_type == MyObjectConnection.Edge

    assert isinstance(pageinfo_field, Field)
    assert isinstance(pageinfo_field.type, NonNull)
    assert pageinfo_field.type.of_type == PageInfo


def test_multiple_connection_edges_are_not_the_same():
    class MyObjectConnection(Connection):
        extra = String()

        class Meta:
            node = MyObject

        class Edge:
            other = String()

    class MyOtherObjectConnection(Connection):
        class Meta:
            node = MyObject

        class Edge:
            other = String()

    assert MyObjectConnection.Edge != MyOtherObjectConnection.Edge
    assert MyObjectConnection.Edge._meta.name != MyOtherObjectConnection.Edge._meta.name


def test_create_connection_with_custom_edge_type():
    class MyEdge(Edge):
        node = Field(MyObject)

    class MyObjectConnection(Connection):
        extra = String()
        edges = List(MyEdge)

    assert MyObjectConnection.Edge == MyEdge
    assert MyObjectConnection._meta.name == 'MyObjectConnection'
    fields = MyObjectConnection._meta.fields
    assert list(fields.keys()) == ['extra', 'edges', 'page_info']
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
    assert list(fields.keys()) == ['extra', 'edges', 'page_info']


def test_defaul_connection_for_type():
    MyObjectConnection = Connection.for_type(MyObject)
    assert MyObjectConnection._meta.name == 'MyObjectConnection'
    fields = MyObjectConnection._meta.fields
    assert list(fields.keys()) == ['edges', 'page_info']


def test_default_connection_for_type_does_not_returns_same_Connection():
    assert Connection.for_type(MyObject) != Connection.for_type(MyObject)


def test_edge():
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


def test_pageinfo():
    assert PageInfo._meta.name == 'PageInfo'
    fields = PageInfo._meta.fields
    assert list(fields.keys()) == ['has_next_page', 'has_previous_page', 'start_cursor', 'end_cursor']


def test_edge_for_node_type():
    edge = Connection.for_type(MyObject).Edge

    assert edge._meta.name == 'MyObjectEdge'
    edge_fields = edge._meta.fields
    assert list(edge_fields.keys()) == ['cursor', 'node']

    assert isinstance(edge_fields['node'], Field)
    assert edge_fields['node'].type == MyObject


def test_edge_for_object_type():
    class MyObject(ObjectType):
        field = String()

    edge = Connection.for_type(MyObject).Edge

    assert edge._meta.name == 'MyObjectEdge'
    edge_fields = edge._meta.fields
    assert list(edge_fields.keys()) == ['cursor', 'node']

    assert isinstance(edge_fields['node'], Field)
    assert edge_fields['node'].type == MyObject


def test_edge_for_type_returns_same_edge():
    MyObjectConnection = Connection.for_type(MyObject)
    assert MyObjectConnection.Edge == MyObjectConnection.Edge
