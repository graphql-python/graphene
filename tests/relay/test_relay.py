from pytest import raises

import graphene
from graphene import relay


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


def test_node_should_have_connection():
    assert OtherNode.connection


def test_node_should_have_id_field():
    assert 'id' in OtherNode._meta.fields_map


def test_field_no_contributed_raises_error():
    with raises(Exception) as excinfo:
        class Ship(graphene.ObjectType):
            name = graphene.StringField()


        class Faction(relay.Node):
            name = graphene.StringField()
            ships = relay.ConnectionField(Ship)

    assert 'same type_name' in str(excinfo.value)
