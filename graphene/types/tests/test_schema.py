from ..scalars import String
from ..field import Field
from ..objecttype import ObjectType, implements
from ..interface import Interface
from ..structures import List
from ..schema import Schema


class Character(Interface):
    name = String()
    friends = List(lambda: Character)


class Pet(ObjectType):
    type = String()


@implements(Character)
class Human(ObjectType):
    pet = Field(Pet)

    def resolve_pet(self, *args):
        return Pet(type='Dog')

    def resolve_friends(self, *args):
        return [Human(name='Peter')]


class RootQuery(ObjectType):
    character = Field(Character)

    def resolve_character(self, *_):
        return Human(name='Harry')


schema = Schema(query=RootQuery, types=[Human])


def test_schema():
    executed = schema.execute('{ character {name, friends { name}, ...on Human {pet { type } } } }')
    assert executed.data == {'character': {'name': 'Harry', 'friends': [{'name': 'Peter'}], 'pet': {'type': 'Dog'}}}


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
  friends: [Character]
}

type Human implements Character {
  name: String
  friends: [Character]
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
