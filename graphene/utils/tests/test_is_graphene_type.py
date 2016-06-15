from graphene.types import ObjectType
from graphql import GraphQLField, GraphQLObjectType, GraphQLString

from ..is_graphene_type import is_graphene_type


def test_is_graphene_type_objecttype():
    class MyObjectType(ObjectType):
        pass

    assert is_graphene_type(MyObjectType)


def test_is_graphene_type_graphqltype():
    MyGraphQLType = GraphQLObjectType('MyGraphQLType', fields={
        'field': GraphQLField(GraphQLString)
    })
    assert not is_graphene_type(MyGraphQLType)


def test_is_graphene_type_other():
    MyObject = object()
    assert not is_graphene_type(MyObject)
