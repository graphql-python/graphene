import pytest

from graphql_relay import to_global_id

from ..node import Node
from ...types import ObjectType, Schema, implements
from ...types.scalars import String


@implements(Node)
class MyNode(ObjectType):
    name = String()

    @staticmethod
    def get_node(id, *_):
        return MyNode(name=str(id))


class RootQuery(ObjectType):
    node = Node.Field

schema = Schema(query=RootQuery, types=[MyNode])


def test_node_no_get_node():
    with pytest.raises(AssertionError) as excinfo:
        @implements(Node)
        class MyNode(ObjectType):
            pass

    assert "MyNode.get_node method is required by the Node interface." == str(excinfo.value)


def test_node_no_get_node():
    with pytest.raises(AssertionError) as excinfo:
        class MyNode(ObjectType):
            class Meta:
                interfaces = [Node]

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
