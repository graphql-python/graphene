from graphql import graphql
from py.test import raises

from graphene import Interface, List, ObjectType, Schema, String
from graphene.core.fields import Field
from graphene.core.types.base import LazyType
from tests.utils import assert_equal_lists

schema = Schema(name='My own schema')


class Character(Interface):
    name = String()


class Pet(ObjectType):
    type = String(resolver=lambda *_: 'Dog')


class Human(Character):
    friends = List(Character)
    pet = Field(Pet)

    def resolve_name(self, *args):
        return 'Peter'

    def resolve_friend(self, *args):
        return Human(object())

    def resolve_pet(self, *args):
        return Pet(object())

schema.query = Human


def test_get_registered_type():
    assert schema.get_type('Character') == Character


def test_get_unregistered_type():
    with raises(Exception) as excinfo:
        schema.get_type('NON_EXISTENT_MODEL')
    assert 'not found' in str(excinfo.value)


def test_schema_query():
    assert schema.query == Human


def test_query_schema_graphql():
    object()
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
    result = graphql(schema.schema, query, root_value=Human(object()))
    assert not result.errors
    assert result.data == expected


def test_query_schema_execute():
    object()
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
    result = schema.execute(query, root_value=object())
    assert not result.errors
    assert result.data == expected


def test_schema_get_type_map():
    assert_equal_lists(
        schema.schema.get_type_map().keys(),
        ['__Field', 'String', 'Pet', 'Character', '__InputValue',
         '__Directive', '__DirectiveLocation', '__TypeKind', '__Schema',
         '__Type', 'Human', '__EnumValue', 'Boolean'])


def test_schema_no_query():
    schema = Schema(name='My own schema')
    with raises(Exception) as excinfo:
        schema.schema
    assert 'define a base query type' in str(excinfo)


def test_auto_camelcase_off():
    schema = Schema(name='My own schema', auto_camelcase=False)

    class Query(ObjectType):
        test_field = String(resolver=lambda *_: 'Dog')

    schema.query = Query

    query = "query {test_field}"
    expected = {"test_field": "Dog"}

    result = graphql(schema.schema, query, root_value=Query(object()))
    assert not result.errors
    assert result.data == expected


def test_schema_register():
    schema = Schema(name='My own schema')

    @schema.register
    class MyType(ObjectType):
        type = String(resolver=lambda *_: 'Dog')

    schema.query = MyType

    assert schema.get_type('MyType') == MyType


def test_schema_register_no_query_type():
    schema = Schema(name='My own schema')

    @schema.register
    class MyType(ObjectType):
        type = String(resolver=lambda *_: 'Dog')

    with raises(Exception) as excinfo:
        schema.get_type('MyType')
    assert 'base query type' in str(excinfo.value)


def test_schema_introspect():
    schema = Schema(name='My own schema')

    class MyType(ObjectType):
        type = String(resolver=lambda *_: 'Dog')

    schema.query = MyType

    introspection = schema.introspect()
    assert '__schema' in introspection


def test_lazytype():
    schema = Schema(name='My own schema')

    t = LazyType('MyType')

    @schema.register
    class MyType(ObjectType):
        type = String(resolver=lambda *_: 'Dog')

    schema.query = MyType

    assert schema.T(t) == schema.T(MyType)


def test_deprecated_plugins_throws_exception():
    with raises(Exception) as excinfo:
        Schema(plugins=[])
    assert 'Plugins are deprecated, please use middlewares' in str(excinfo.value)


def test_schema_str():
    expected = """
schema {
  query: Human
}

interface Character {
  name: String
}

type Human implements Character {
  name: String
  friends: [Character]
  pet: Pet
}

type Pet {
  type: String
}
""".lstrip()
    assert str(schema) == expected
