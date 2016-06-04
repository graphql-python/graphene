from graphql import graphql

from ..node import Node
from ...types import ObjectType, Schema, implements
from ...types.scalars import String, Int


class CustomNode(Node):
    @staticmethod
    def get_node(id, context, info):
        assert info.schema == schema
        if id in user_data:
            return user_data.get(id)
        else:
            return photo_data.get(id)


@implements(CustomNode)
class User(ObjectType):
    name = String()


@implements(CustomNode)
class Photo(ObjectType):
    width = Int()


user_data = {
    '1': User(id='1', name='John Doe'),
    '2': User(id='2', name='Jane Smith'),
}

photo_data = {
    '3': Photo(id='3', width=300),
    '4': Photo(id='4', width=400),
}


class RootQuery(ObjectType):
    node = CustomNode.Field

schema = Schema(query=RootQuery, types=[User, Photo])


def test_gets_the_correct_id_for_users():
    query = '''
      {
        node(id: "1") {
          id
        }
      }
    '''
    expected = {
        'node': {
            'id': '1',
        }
    }
    result = graphql(schema, query)
    assert not result.errors
    assert result.data == expected


def test_gets_the_correct_id_for_photos():
    query = '''
      {
        node(id: "4") {
          id
        }
      }
    '''
    expected = {
        'node': {
            'id': '4',
        }
    }
    result = graphql(schema, query)
    assert not result.errors
    assert result.data == expected


def test_gets_the_correct_name_for_users():
    query = '''
      {
        node(id: "1") {
          id
          ... on User {
            name
          }
        }
      }
    '''
    expected = {
        'node': {
            'id': '1',
            'name': 'John Doe'
        }
    }
    result = graphql(schema, query)
    assert not result.errors
    assert result.data == expected


def test_gets_the_correct_width_for_photos():
    query = '''
      {
        node(id: "4") {
          id
          ... on Photo {
            width
          }
        }
      }
    '''
    expected = {
        'node': {
            'id': '4',
            'width': 400
        }
    }
    result = graphql(schema, query)
    assert not result.errors
    assert result.data == expected


def test_gets_the_correct_typename_for_users():
    query = '''
      {
        node(id: "1") {
          id
          __typename
        }
      }
    '''
    expected = {
        'node': {
            'id': '1',
            '__typename': 'User'
        }
    }
    result = graphql(schema, query)
    assert not result.errors
    assert result.data == expected


def test_gets_the_correct_typename_for_photos():
    query = '''
      {
        node(id: "4") {
          id
          __typename
        }
      }
    '''
    expected = {
        'node': {
            'id': '4',
            '__typename': 'Photo'
        }
    }
    result = graphql(schema, query)
    assert not result.errors
    assert result.data == expected


def test_ignores_photo_fragments_on_user():
    query = '''
      {
        node(id: "1") {
          id
          ... on Photo {
            width
          }
        }
      }
    '''
    expected = {
        'node': {
            'id': '1',
        }
    }
    result = graphql(schema, query)
    assert not result.errors
    assert result.data == expected


def test_returns_null_for_bad_ids():
    query = '''
      {
        node(id: "5") {
          id
        }
      }
    '''
    expected = {
        'node': None
    }
    result = graphql(schema, query)
    assert not result.errors
    assert result.data == expected


def test_have_correct_node_interface():
    query = '''
      {
        __type(name: "Node") {
          name
          kind
          fields {
            name
            type {
              kind
              ofType {
                name
                kind
              }
            }
          }
        }
      }
    '''
    expected = {
        '__type': {
          'name': 'Node',
          'kind': 'INTERFACE',
          'fields': [
            {
              'name': 'id',
              'type': {
                'kind': 'NON_NULL',
                'ofType': {
                  'name': 'ID',
                  'kind': 'SCALAR'
                }
              }
            }
          ]
        }
    }
    result = graphql(schema, query)
    assert not result.errors
    assert result.data == expected


def test_has_correct_node_root_field():
    query = '''
      {
        __schema {
          queryType {
            fields {
              name
              type {
                name
                kind
              }
              args {
                name
                type {
                  kind
                  ofType {
                    name
                    kind
                  }
                }
              }
            }
          }
        }
      }
    '''
    expected = {
        '__schema': {
          'queryType': {
            'fields': [
              {
                'name': 'node',
                'type': {
                  'name': 'Node',
                  'kind': 'INTERFACE'
                },
                'args': [
                  {
                    'name': 'id',
                    'type': {
                      'kind': 'NON_NULL',
                      'ofType': {
                        'name': 'ID',
                        'kind': 'SCALAR'
                      }
                    }
                  }
                ]
              }
            ]
          }
        }
    }
    result = graphql(schema, query)
    assert not result.errors
    assert result.data == expected
