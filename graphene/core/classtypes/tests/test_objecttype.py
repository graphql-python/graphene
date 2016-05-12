from graphql.type import GraphQLObjectType
from py.test import raises

from graphene.core.schema import Schema
from graphene.core.types import String

from ..objecttype import ObjectType
from ..uniontype import UnionType


def test_object_type():
    class Human(ObjectType):
        '''Human description'''
        name = String()
        friends = String()

    schema = Schema()

    object_type = schema.T(Human)
    assert Human._meta.type_name == 'Human'
    assert isinstance(object_type, GraphQLObjectType)
    assert object_type.description == 'Human description'
    assert list(object_type.get_fields().keys()) == ['name', 'friends']
    assert Human._meta.fields_map['name'].object_type == Human


def test_object_type_container():
    class Human(ObjectType):
        name = String()
        friends = String()

    h = Human(name='My name')
    assert h.name == 'My name'


def test_object_type_set_properties():
    class Human(ObjectType):
        name = String()
        friends = String()

        @property
        def readonly_prop(self):
            return 'readonly'

        @property
        def write_prop(self):
            return self._write_prop

        @write_prop.setter
        def write_prop(self, value):
            self._write_prop = value

    h = Human(readonly_prop='custom', write_prop='custom')
    assert h.readonly_prop == 'readonly'
    assert h.write_prop == 'custom'


def test_object_type_container_invalid_kwarg():
    class Human(ObjectType):
        name = String()

    with raises(TypeError):
        Human(invalid='My name')


def test_object_type_container_too_many_args():
    class Human(ObjectType):
        name = String()

    with raises(IndexError):
        Human('Peter', 'No friends :(', None)


def test_object_type_union():
    class Human(ObjectType):
        name = String()

    class Pet(ObjectType):
        name = String()

    class Thing(Human, Pet):
        '''Thing union description'''
        my_attr = True

    assert issubclass(Thing, UnionType)
    assert Thing._meta.types == [Human, Pet]
    assert Thing._meta.type_name == 'Thing'
    assert Thing._meta.description == 'Thing union description'
    assert Thing.my_attr


def test_object_type_not_union_if_abstract():
    schema = Schema()

    class Query1(ObjectType):
        field1 = String()

        class Meta:
            abstract = True

    class Query2(ObjectType):
        field2 = String()

        class Meta:
            abstract = True

    class Query(Query1, Query2):
        '''Query description'''
        my_attr = True

    object_type = schema.T(Query)
    assert issubclass(Query, ObjectType)
    assert Query._meta.type_name == 'Query'
    assert Query._meta.description == 'Query description'
    assert isinstance(object_type, GraphQLObjectType)
    assert list(Query._meta.fields_map.keys()) == ['field1', 'field2']
