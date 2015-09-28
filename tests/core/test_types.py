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

def test_interface():
    object_type = Character._meta.type
    assert Character._meta.interface == True
    assert Character._meta.type_name == 'core.Character'
    assert isinstance(object_type, GraphQLInterfaceType)
    assert object_type.description == 'Character description'
    assert object_type.get_fields() == {'name': Character._meta.fields_map['name'].field}

def test_object_type():
    object_type = Human._meta.type
    assert Human._meta.interface == False
    assert Human._meta.type_name == 'core.Human'
    assert isinstance(object_type, GraphQLObjectType)
    assert object_type.description == 'Human description'
    assert object_type.get_fields() == {'name': Character._meta.fields_map['name'].field, 'friends': Human._meta.fields_map['friends'].field}
    assert object_type.get_interfaces() == [Character._meta.type]
