from graphql import GraphQLObjectType, GraphQLField, GraphQLString

from ..is_graphene_type import is_graphene_type

from graphene.types import ObjectType


def test_is_graphene_type_objecttype():
    assert is_graphene_type(ObjectType)


def test_is_graphene_type_graphqltype():
    MyGraphQLType = GraphQLObjectType('MyGraphQLType', fields={
        'field': GraphQLField(GraphQLString)
    })
    assert not is_graphene_type(MyGraphQLType)


def test_is_graphene_type_other():
    MyObject = object()
    assert not is_graphene_type(MyObject)
