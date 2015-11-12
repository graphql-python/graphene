from pytest import raises

import graphene
from graphene import relay

schema = graphene.Schema()


class OtherNode(relay.Node):
    name = graphene.StringField()

    @classmethod
    def get_node(cls, id):
        pass


def test_field_no_contributed_raises_error():
    with raises(Exception) as excinfo:
        class Part(relay.Node):
            x = graphene.StringField()

    assert 'get_node' in str(excinfo.value)


def test_node_should_have_same_connection_always():
    object()
    connection1 = relay.Connection.for_node(OtherNode)
    connection2 = relay.Connection.for_node(OtherNode)

    assert connection1 == connection2


def test_node_should_have_id_field():
    assert 'id' in OtherNode._meta.fields_map
