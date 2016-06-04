import pytest
from ..scalars import Scalar, String, Int, Float, Boolean
from ..field import Field
from ..objecttype import ObjectType, implements
from ..interface import Interface
from ..schema import Schema


class Character(Interface):
    name = String()


class Pet(ObjectType):
    type = String()


@implements(Character)
class Human(ObjectType):
    pet = Field(Pet)

    def resolve_pet(self, *args):
        return Pet(type='Dog')


class RootQuery(ObjectType):
    character = Field(Character)

    def resolve_character(self, *_):
        return Human(name='Hey!')


schema = Schema(query=RootQuery, types=[Human])


def test_schema():
    executed = schema.execute('{ character {name, ...on Human {pet { type } } } }')
    assert executed.data == {'character': {'name': 'Hey!', 'pet': {'type': 'Dog'}}}


def test_schema_introspect():
    introspection = schema.introspect()
    assert '__schema' in introspection


def test_schema_str():
    expected = """
schema {
  query: RootQuery
}

interface Character {
  name: String
}

type Human implements Character {
  name: String
  pet: Pet
}

type Pet {
  type: String
}

type RootQuery {
  character: Character
}
""".lstrip()
    assert str(schema) == expected


def test_schema_get_type():
    pet = schema.get_type('Pet')
    assert pet == Pet._meta.graphql_type


def test_schema_lazy_type():
    pet = schema.lazy('Pet')
    assert pet() == Pet._meta.graphql_type
