from ..field import Field
from ..interface import Interface
from ..objecttype import ObjectType
from ..scalars import String
from ..schema import Schema
from ..structures import List


class Character(Interface):
    name = String()
    friends = List(lambda: Character)
    best_friend = Field(lambda: Character)


class Pet(ObjectType):
    type = String()


# @implements(Character)
class Human(ObjectType):

    class Meta:
        interfaces = [Character]

    pet = Field(Pet)

    def resolve_pet(self, *args):
        return Pet(type='Dog')

    def resolve_friends(self, *args):
        return [Human(name='Peter')]

    def resolve_best_friend(self, *args):
        return Human(name='Best')


class RootQuery(ObjectType):
    character = Field(Character)

    def resolve_character(self, *_):
        return Human(name='Harry')


schema = Schema(query=RootQuery, types=[Human])


def test_schema():
    executed = schema.execute(
        '{ character {name, bestFriend { name }, friends { name}, ...on Human {pet { type } } } }')
    assert not executed.errors
    assert executed.data == {'character': {'name': 'Harry', 'bestFriend': {
        'name': 'Best'}, 'friends': [{'name': 'Peter'}], 'pet': {'type': 'Dog'}}}


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
  bestFriend: Character
}

type Human implements Character {
  name: String
  friends: [Character]
  bestFriend: Character
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
