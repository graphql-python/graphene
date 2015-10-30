from py.test import raises
from pytest import raises
from graphene.core.fields import (
    IntField,
    StringField,
)
from graphql.core.execution.middlewares.utils import (
    tag_resolver,
    resolver_has_tag
)
from graphql.core.type import (
    GraphQLObjectType,
    GraphQLInterfaceType
)

from graphene.core.types import (
    Interface
)
from graphene.core.schema import Schema


class Character(Interface):
    '''Character description'''
    name = StringField()

    class Meta:
        type_name = 'core_Character'


class Human(Character):
    '''Human description'''
    friends = StringField()

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
        c = Character()
    assert 'An interface cannot be initialized' == str(excinfo.value)


def test_interface_resolve_type():
    resolve_type = Character.resolve_type(schema, Human(object()))
    assert isinstance(resolve_type, GraphQLObjectType)


def test_object_type():
    object_type = schema.T(Human)
    assert Human._meta.is_interface is False
    assert Human._meta.type_name == 'core_Human'
    assert isinstance(object_type, GraphQLObjectType)
    assert object_type.description == 'Human description'
    assert list(object_type.get_fields().keys()) == ['name', 'friends']
    # assert object_type.get_fields() == {'name': Human._meta.fields_map['name'].internal_field(
    #     schema), 'friends': Human._meta.fields_map['friends'].internal_field(schema)}
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
            name = IntField()

    assert 'clashes' in str(excinfo.value)


def test_fields_inherited_should_be_different():
    assert Character._meta.fields_map['name'] != Human._meta.fields_map['name']


def test_field_mantain_resolver_tags():
    class Droid(Character):
        name = StringField()

        def resolve_name(self, *args):
            return 'My Droid'

        tag_resolver(resolve_name, 'test')

    field = Droid._meta.fields_map['name'].internal_field(schema)
    assert resolver_has_tag(field.resolver, 'test')
