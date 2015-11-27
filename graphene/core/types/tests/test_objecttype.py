from graphql.core.execution.middlewares.utils import (resolver_has_tag,
                                                      tag_resolver)
from graphql.core.type import (GraphQLInterfaceType, GraphQLObjectType,
                               GraphQLUnionType)
from py.test import raises

from graphene.core.schema import Schema
from graphene.core.types import Int, Interface, String


class Character(Interface):
    '''Character description'''
    name = String()

    class Meta:
        type_name = 'core_Character'


class Human(Character):
    '''Human description'''
    friends = String()

    class Meta:
        type_name = 'core_Human'

    @property
    def readonly_prop(self):
        return 'readonly'

    @property
    def write_prop(self):
        return self._write_prop

    @write_prop.setter
    def write_prop(self, value):
        self._write_prop = value


class Droid(Character):
    '''Droid description'''


class CharacterType(Droid, Human):
    '''Union Type'''

schema = Schema()


def test_interface():
    object_type = schema.T(Character)
    assert Character._meta.is_interface is True
    assert isinstance(object_type, GraphQLInterfaceType)
    assert Character._meta.type_name == 'core_Character'
    assert object_type.description == 'Character description'
    assert list(object_type.get_fields().keys()) == ['name']


def test_interface_cannot_initialize():
    with raises(Exception) as excinfo:
        Character()
    assert 'An interface cannot be initialized' == str(excinfo.value)


def test_union():
    object_type = schema.T(CharacterType)
    assert CharacterType._meta.is_union is True
    assert isinstance(object_type, GraphQLUnionType)
    assert object_type.description == 'Union Type'


def test_union_cannot_initialize():
    with raises(Exception) as excinfo:
        CharacterType()
    assert 'An union cannot be initialized' == str(excinfo.value)


def test_interface_resolve_type():
    resolve_type = Character._resolve_type(schema, Human(object()))
    assert isinstance(resolve_type, GraphQLObjectType)


def test_object_type():
    object_type = schema.T(Human)
    assert Human._meta.is_interface is False
    assert Human._meta.type_name == 'core_Human'
    assert isinstance(object_type, GraphQLObjectType)
    assert object_type.description == 'Human description'
    assert list(object_type.get_fields().keys()) == ['name', 'friends']
    assert object_type.get_interfaces() == [schema.T(Character)]
    assert Human._meta.fields_map['name'].object_type == Human


def test_object_type_container():
    h = Human(name='My name')
    assert h.name == 'My name'


def test_object_type_set_properties():
    h = Human(readonly_prop='custom', write_prop='custom')
    assert h.readonly_prop == 'readonly'
    assert h.write_prop == 'custom'


def test_object_type_container_invalid_kwarg():
    with raises(TypeError):
        Human(invalid='My name')


def test_object_type_container_too_many_args():
    with raises(IndexError):
        Human('Peter', 'No friends :(', None)


def test_field_clashes():
    with raises(Exception) as excinfo:
        class Droid(Character):
            name = Int()

    assert 'clashes' in str(excinfo.value)


def test_fields_inherited_should_be_different():
    assert Character._meta.fields_map['name'] != Human._meta.fields_map['name']


def test_field_mantain_resolver_tags():
    class Droid(Character):
        name = String()

        def resolve_name(self, *args):
            return 'My Droid'

        tag_resolver(resolve_name, 'test')

    field = schema.T(Droid._meta.fields_map['name'])
    assert resolver_has_tag(field.resolver, 'test')


def test_type_has_nonnull():
    class Droid(Character):
        name = String()

    assert Droid.NonNull.of_type == Droid


def test_type_has_list():
    class Droid(Character):
        name = String()

    assert Droid.List.of_type == Droid
