import pytest

from graphql_relay import to_global_id

from ...types import ObjectType, Schema, String
from ..connection import Connection
from ..node import Node


class SharedNodeFields(ObjectType):

    class Meta:
        interfaces = (Node, )

    shared = String()
    something_else = String()

    @classmethod
    def get_node(cls, id, *_):
        return cls(shared=str(id))


class MyNode(ObjectType):

    class Meta:
        interfaces = (Node, )
    name = String()

    @staticmethod
    def get_node(id, *_):
        return MyNode(name=str(id))


class MyOtherNode(SharedNodeFields):
    extra_field = String()

    def resolve_extra_field(self, *_):
        return 'extra field info.'


class RootQuery(ObjectType):
    first = String()
    node = Node.Field()

schema = Schema(query=RootQuery, types=[MyNode, MyOtherNode])


def test_node_no_get_node():
    with pytest.raises(AssertionError) as excinfo:
        class MyNode(ObjectType):

            class Meta:
                interfaces = (Node, )

    assert "MyNode.get_node method is required by the Node interface." == str(excinfo.value)


def test_node_no_get_node_with_meta():
    with pytest.raises(AssertionError) as excinfo:
        class MyNode(ObjectType):

            class Meta:
                interfaces = (Node, )

    assert "MyNode.get_node method is required by the Node interface." == str(excinfo.value)


def test_node_good():
    assert 'id' in MyNode._meta.fields


def test_node_get_connection():
    connection = MyNode.Connection
    assert issubclass(connection, Connection)


def test_node_get_connection_dont_duplicate():
    assert MyNode.Connection == MyNode.Connection


def test_node_query():
    executed = schema.execute(
        '{ node(id:"%s") { ... on MyNode { name } } }' % to_global_id("MyNode", 1)
    )
    assert not executed.errors
    assert executed.data == {'node': {'name': '1'}}


def test_subclassed_node_query():
    executed = schema.execute(
        '{ node(id:"%s") { ... on MyOtherNode { shared, extraField } } }' % to_global_id("MyOtherNode", 1)
    )
    assert not executed.errors
    assert executed.data == {'node': {'shared': '1', 'extraField': 'extra field info'}}


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

type MyOtherNode implements Node {
  shared: String
  somethingElse: String
  extraField: String
}

interface Node {
  id: ID!
}

type RootQuery {
  first: String
  node(id: ID!): Node
}
""".lstrip()
