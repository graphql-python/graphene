from pytest import raises

import graphene
from graphene import relay

schema = graphene.Schema()


class MyType(object):
    name = 'my'


class MyNode(relay.Node):
    name = graphene.StringField()

    @classmethod
    def get_node(cls, id):
        return MyNode(MyType())


class Query(graphene.ObjectType):
    my_node = relay.NodeField(MyNode)


schema.query = Query


def test_nodefield_query():
    query = '''
    query RebelsShipsQuery {
      myNode(id:"TXlOb2RlOjE=") {
        name
      }
    }
    '''
    expected = {
        'myNode': {
            'name': 'my'
        }
    }
    result = schema.execute(query)
    assert not result.errors
    assert result.data == expected
