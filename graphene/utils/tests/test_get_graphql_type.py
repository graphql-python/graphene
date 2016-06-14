import pytest

from graphql.type.definition import is_type
from graphql import GraphQLObjectType, GraphQLField, GraphQLString

from graphene.types import ObjectType
from ..get_graphql_type import get_graphql_type


MyGraphQLType = GraphQLObjectType('MyGraphQLType', fields={
    'field': GraphQLField(GraphQLString)
})


def test_get_graphql_type_graphene():
    class MyGrapheneType(ObjectType):
        pass

    assert is_type(get_graphql_type(MyGrapheneType))


def test_get_graphql_type_custom_graphene_type():
    class MyGrapheneType(ObjectType):
        class Meta:
            graphql_type = MyGraphQLType

    assert get_graphql_type(MyGrapheneType) == MyGraphQLType


def test_get_graphql_type_graphql_type():
    assert get_graphql_type(MyGraphQLType) == MyGraphQLType


def test_get_graphql_type_unknown_type():
    with pytest.raises(Exception) as excinfo:
        get_graphql_type(object)

    assert "Cannot get GraphQL type of <type 'object'>." == str(excinfo.value)
