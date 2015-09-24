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

class Human(Character):
    '''Human description'''
    friends = StringField()

def test_interface():
    object_type = Character._meta.type
    assert Character._meta.interface == True
    assert Character._meta.type_name == 'Character'
    assert isinstance(object_type, GraphQLInterfaceType)
    assert object_type.description == 'Character description'
    assert object_type.get_fields() == {'name': Character.name.field}

def test_object_type():
    object_type = Human._meta.type
    assert Human._meta.interface == False
    assert Human._meta.type_name == 'Human'
    assert isinstance(object_type, GraphQLObjectType)
    assert object_type.description == 'Human description'
    assert object_type.get_fields() == {'name': Character.name.field, 'friends': Human.friends.field}
    assert object_type.get_interfaces() == [Character._meta.type]
