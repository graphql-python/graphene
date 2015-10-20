from pytest import raises
from graphql.core.type import (
    GraphQLNonNull,
    GraphQLID
)

import graphene
from graphene import relay

schema = graphene.Schema()


class MyType(object):
    name = 'my'
    arg = None


class MyConnection(relay.Connection):
    my_custom_field = graphene.StringField(resolve=lambda instance, *_: 'Custom')


class MyNode(relay.Node):
    name = graphene.StringField()

    @classmethod
    def get_node(cls, id):
        return MyNode(MyType())


class Query(graphene.ObjectType):
    my_node = relay.NodeField(MyNode)
    all_my_nodes = relay.ConnectionField(MyNode, connection_type=MyConnection, customArg=graphene.Argument(graphene.String))

    def resolve_all_my_nodes(self, args, info):
        t = MyType()
        custom_arg = args.get('customArg')
        assert custom_arg == "1"
        return [MyNode(t)]

schema.query = Query


def test_nodefield_query():
    query = '''
    query RebelsShipsQuery {
      myNode(id:"TXlOb2RlOjE=") {
        name
      },
      allMyNodes (customArg:"1") {
        edges {
          node {
            name
          }
        },
        myCustomField
        pageInfo {
          hasNextPage
        }
      }
    }
    '''
    expected = {
        'myNode': {
            'name': 'my'
        },
        'allMyNodes': {
            'edges': [{
                'node': {
                    'name': 'my'
                }
            }],
            'myCustomField': 'Custom',
            'pageInfo': {
                'hasNextPage': False,
            }
        }
    }
    result = schema.execute(query)
    assert not result.errors
    assert result.data == expected


def test_nodeidfield():
    id_field = MyNode._meta.fields_map['id']
    assert isinstance(id_field.internal_field(schema).type, GraphQLNonNull)
    assert id_field.internal_field(schema).type.of_type == GraphQLID
