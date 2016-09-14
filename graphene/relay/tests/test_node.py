from collections import OrderedDict
import pytest

from graphql_relay import to_global_id

from ...types import ObjectType, Schema, String, AbstractType
from ..connection import Connection
from ..node import Node


class SharedNodeFields(AbstractType):

    shared = String()
    something_else = String()

    def resolve_something_else(*_):
        return '----'


class MyNode(ObjectType):

    class Meta:
        interfaces = (Node, )
    name = String()

    @staticmethod
    def get_node(id, *_):
        return MyNode(name=str(id))


class MyOtherNode(SharedNodeFields, ObjectType):
    extra_field = String()

    class Meta:
        interfaces = (Node, )

    def resolve_extra_field(self, *_):
        return 'extra field info.'

    @staticmethod
    def get_node(id, *_):
        return MyOtherNode(shared=str(id))


class RootQuery(ObjectType):
    first = String()
    node = Node.Field()

schema = Schema(query=RootQuery, types=[MyNode, MyOtherNode])


def test_node_good():
    assert 'id' in MyNode._meta.fields


def test_node_query():
    executed = schema.execute(
        '{ node(id:"%s") { ... on MyNode { name } } }' % to_global_id("MyNode", 1)
    )
    assert not executed.errors
    assert executed.data == {'node': {'name': '1'}}


def test_subclassed_node_query():
    executed = schema.execute(
        '{ node(id:"%s") { ... on MyOtherNode { shared, extraField, somethingElse } } }' % to_global_id("MyOtherNode", 1)
    )
    assert not executed.errors
    assert executed.data == OrderedDict({'node': OrderedDict([('shared', '1'), ('extraField', 'extra field info.'), ('somethingElse', '----')])})


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
  id: ID!
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
