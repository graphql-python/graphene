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


def test_nodeidfield():
    id_field = MyNode._meta.fields_map['id']
    assert isinstance(id_field.internal_field(schema).type, GraphQLNonNull)
    assert id_field.internal_field(schema).type.of_type == GraphQLID
