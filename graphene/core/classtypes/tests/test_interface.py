from graphql.type import GraphQLInterfaceType, GraphQLObjectType
from py.test import raises

from graphene.core.schema import Schema
from graphene.core.types import String

from ..interface import Interface
from ..objecttype import ObjectType


def test_interface():
    class Character(Interface):
        '''Character description'''
        name = String()

    schema = Schema()

    object_type = schema.T(Character)
    assert issubclass(Character, Interface)
    assert isinstance(object_type, GraphQLInterfaceType)
    assert Character._meta.interface
    assert Character._meta.type_name == 'Character'
    assert object_type.description == 'Character description'
    assert list(object_type.get_fields().keys()) == ['name']


def test_interface_cannot_initialize():
    class Character(Interface):
        pass

    with raises(Exception) as excinfo:
        Character()
    assert 'An interface cannot be initialized' == str(excinfo.value)


def test_interface_inheritance_abstract():
    class Character(Interface):
        pass

    class ShouldBeInterface(Character):

        class Meta:
            abstract = True

    class ShouldBeObjectType(ShouldBeInterface):
        pass

    assert ShouldBeInterface._meta.interface
    assert not ShouldBeObjectType._meta.interface
    assert issubclass(ShouldBeObjectType, ObjectType)


def test_interface_inheritance():
    class Character(Interface):
        pass

    class GeneralInterface(Interface):
        pass

    class ShouldBeObjectType(GeneralInterface, Character):
        pass

    schema = Schema()

    assert Character._meta.interface
    assert not ShouldBeObjectType._meta.interface
    assert issubclass(ShouldBeObjectType, ObjectType)
    assert Character in ShouldBeObjectType._meta.interfaces
    assert GeneralInterface in ShouldBeObjectType._meta.interfaces
    assert isinstance(schema.T(Character), GraphQLInterfaceType)
    assert isinstance(schema.T(ShouldBeObjectType), GraphQLObjectType)


def test_interface_inheritance_non_objects():
    class CommonClass(object):
        common_attr = True

    class Character(CommonClass, Interface):
        pass

    class ShouldBeObjectType(Character):
        pass

    assert Character._meta.interface
    assert Character.common_attr
    assert ShouldBeObjectType.common_attr
