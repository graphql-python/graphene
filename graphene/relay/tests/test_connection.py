
from ...types import ObjectType, Schema
from ...types.field import Field
from ...types.scalars import String
from ..connection import Connection
from ..node import Node


class MyObject(Node, ObjectType):
    field = String()

    @classmethod
    def get_node(cls, id):
        pass


class MyObjectConnection(Connection):

    class Meta:
        node = MyObject

    class Edge:
        other = String()


class RootQuery(ObjectType):
    my_connection = Field(MyObjectConnection)


schema = Schema(query=RootQuery)


def test_node_good():
    graphql_type = MyObjectConnection._meta.graphql_type
    fields = graphql_type.get_fields()
    assert 'edges' in fields
    assert 'pageInfo' in fields
    edge_fields = fields['edges'].type.of_type.get_fields()
    assert 'node' in edge_fields
    assert edge_fields['node'].type == MyObject._meta.graphql_type
    assert 'other' in edge_fields
