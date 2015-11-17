from graphql.core.type import GraphQLID, GraphQLNonNull

import graphene
from graphene import relay

schema = graphene.Schema()


class MyConnection(relay.Connection):
    my_custom_field = graphene.String(
        resolver=lambda instance, *_: 'Custom')


class MyNode(relay.Node):
    name = graphene.String()

    @classmethod
    def get_node(cls, id):
        return MyNode(id=id, name='mo')


class Query(graphene.ObjectType):
    my_node = relay.NodeField(MyNode)
    all_my_nodes = relay.ConnectionField(
        MyNode, connection_type=MyConnection, customArg=graphene.String())

    def resolve_all_my_nodes(self, args, info):
        custom_arg = args.get('customArg')
        assert custom_arg == "1"
        return [MyNode(name='my')]

schema.query = Query


def test_nodefield_query():
    query = '''
    query RebelsShipsQuery {
      myNode(id:"TXlOb2RlOjE=") {
        id
        name
      },
      false: myNode(id:"WrongNodeId") {
        id
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
            'id': 'TXlOb2RlOjE=',
            'name': 'mo'
        },
        'false': None,
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
    id_field_type = schema.T(id_field)
    assert isinstance(id_field_type.type, GraphQLNonNull)
    assert id_field_type.type.of_type == GraphQLID
