import pytest

from graphql_relay import to_global_id

from ...types import ObjectType, Schema
from ...types.scalars import String
from ..node import Node


class MyNode(Node, ObjectType):

    name = String()

    @staticmethod
    def get_node(id, *_):
        return MyNode(name=str(id))


class RootQuery(ObjectType):
    first = String()
    node = Node.Field()

schema = Schema(query=RootQuery, types=[MyNode])


def test_node_no_get_node():
    with pytest.raises(AssertionError) as excinfo:
        class MyNode(Node, ObjectType):
            pass

    assert "MyNode.get_node method is required by the Node interface." == str(excinfo.value)


def test_node_no_get_node_with_meta():
    with pytest.raises(AssertionError) as excinfo:
        class MyNode(Node, ObjectType):
            pass

    assert "MyNode.get_node method is required by the Node interface." == str(excinfo.value)


def test_node_good():
    graphql_type = MyNode._meta.graphql_type
    assert 'id' in graphql_type.get_fields()


def test_node_query():
    executed = schema.execute(
        '{ node(id:"%s") { ... on MyNode { name } } }' % to_global_id("MyNode", 1)
    )
    assert not executed.errors
    assert executed.data == {'node': {'name': '1'}}


def test_node_query_incorrect_id():
    executed = schema.execute(
        '{ node(id:"%s") { ... on MyNode { name } } }' % "something:2"
    )
    assert not executed.errors
    assert executed.data == {'node': None}


def test_str_schema():
    assert str(schema) == """
schema {
  query: RootQuery
}

type MyNode implements Node {
  id: ID!
  name: String
}

interface Node {
  id: ID!
}

type RootQuery {
  first: String
  node(id: ID!): Node
}
""".lstrip()
