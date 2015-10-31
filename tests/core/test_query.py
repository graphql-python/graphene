

from graphene.core.fields import Field, ListField, StringField
from graphene.core.schema import Schema
from graphene.core.types import Interface, ObjectType
from graphql.core import graphql
from graphql.core.type import (GraphQLInterfaceType, GraphQLObjectType,
                               GraphQLSchema)


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


schema = Schema()

Human_type = schema.T(Human)


def test_type():
    assert Human._meta.fields_map['name'].resolve(
        Human(object()), None, None) == 'Peter'


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
