from py.test import raises
from collections import namedtuple
from pytest import raises
from graphql.core import graphql
from graphene.core.fields import (
    Field,
    StringField,
    ListField,
)
from graphql.core.type import (
    GraphQLObjectType,
    GraphQLSchema,
    GraphQLInterfaceType
)

from graphene.core.types import (
    Interface,
    ObjectType
)


class Character(Interface):
    name = StringField()


class Pet(ObjectType):
    type = StringField(resolve=lambda *_: 'Dog')


class Human(Character):
    friends = ListField(Character)
    pet = Field(Pet)

    def resolve_name(self, *args):
        return 'Peter'

    def resolve_friend(self, *args):
        return Human(object())

    def resolve_pet(self, *args):
        return Pet(object())
    # def resolve_friends(self, *args, **kwargs):
    #     return 'HEY YOU!'

schema = object()

Human_type = Human.internal_type(schema)


def test_query():
    schema = GraphQLSchema(query=Human_type)
    query = '''
    {
      name
      pet {
        type
      }
    }
    '''
    expected = {
        'name': 'Peter',
        'pet': {
            'type': 'Dog'
        }
    }
    result = graphql(schema, query, root=Human(object()))
    assert not result.errors
    assert result.data == expected
