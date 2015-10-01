from py.test import raises
from collections import namedtuple
from pytest import raises
from graphene.core.fields import (
    Field,
    StringField,
)
from graphql.core.type import (
    GraphQLObjectType,
    GraphQLInterfaceType
)

from graphene.core.types import (
    Interface,
    ObjectType
)


class Character(Interface):
    '''Character description'''
    name = StringField()
    class Meta:
        type_name = 'core.Character'


class Human(Character):
    '''Human description'''
    friends = StringField()

    class Meta:
        type_name = 'core.Human'

schema = object()


def test_interface():
    object_type = Character.internal_type(schema)
    assert Character._meta.interface == True
    assert isinstance(object_type, GraphQLInterfaceType)
    assert Character._meta.type_name == 'core.Character'
    assert object_type.description == 'Character description'
    assert object_type.get_fields() == {'name': Character._meta.fields_map['name'].internal_field(schema)}


def test_interface_resolve_type():
    resolve_type = Character.resolve_type(schema, Human(object()))
    assert isinstance(resolve_type, GraphQLObjectType)


def test_object_type():
    object_type = Human.internal_type(schema)
    assert Human._meta.interface == False
    assert Human._meta.type_name == 'core.Human'
    assert isinstance(object_type, GraphQLObjectType)
    assert object_type.description == 'Human description'
    assert object_type.get_fields() == {'name': Character._meta.fields_map['name'].internal_field(schema), 'friends': Human._meta.fields_map['friends'].internal_field(schema)}
    assert object_type.get_interfaces() == [Character.internal_type(schema)]
