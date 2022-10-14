from textwrap import dedent

from pytest import raises

from graphql.type import GraphQLObjectType, GraphQLSchema

from ..field import Field
from ..mutation import Mutation
from ..objecttype import ObjectType
from ..scalars import Int, String
from ..schema import Schema


class MyType(ObjectType):
    field = String()


class MyOtherType(ObjectType):
    field = String()
    my_type = Field(MyType)


class Query(ObjectType):
    inner = Field(MyOtherType)


class CreateUser(Mutation):
    class Arguments:
        name = String()

    name = String()

    def mutate(self, info, name):
        return CreateUser(name=name)


class Mutation(ObjectType):
    create_user = CreateUser.Field()


class Subscription(ObjectType):
    count_to_ten = Field(Int)


def test_schema():
    schema = Schema(Query)
    graphql_schema = schema.graphql_schema
    assert isinstance(graphql_schema, GraphQLSchema)
    query_type = graphql_schema.query_type
    assert isinstance(query_type, GraphQLObjectType)
    assert query_type.name == "Query"
    assert query_type.graphene_type is Query


def test_schema_get_type():
    schema = Schema(Query)
    assert schema.Query == Query
    assert schema.MyOtherType == MyOtherType


def test_schema_get_type_error():
    schema = Schema(Query)
    with raises(AttributeError) as exc_info:
        schema.X

    assert str(exc_info.value) == 'Type "X" not found in the Schema'


def test_schema_str():
    schema = Schema(Query)
    assert (
        str(schema).strip()
        == dedent(
            """
        type Query {
          inner: MyOtherType
        }

        type MyOtherType {
          field: String
          myType: MyType
        }

        type MyType {
          field: String
        }
        """
        ).strip()
    )


def test_schema_introspect():
    schema = Schema(Query)
    assert "__schema" in schema.introspect()


def test_schema_requires_query_type():
    schema = Schema()
    result = schema.execute("query {}")

    assert len(result.errors) == 1
    error = result.errors[0]
    assert error.message == "Query root type must be provided."


def test_schema_object_type_name_prefix_camelcase():
    schema = Schema(
        Query,
        Mutation,
        Subscription,
        auto_camelcase=True,
        object_type_name_prefix="prefix",
    )
    assert (
        str(schema).strip()
        == dedent(
            """
        schema {
          query: PrefixQuery
          mutation: PrefixMutation
          subscription: PrefixSubscription
        }

        type PrefixQuery {
          prefixInner: PrefixMyOtherType
        }

        type PrefixMyOtherType {
          field: String
          myType: PrefixMyType
        }

        type PrefixMyType {
          field: String
        }

        type PrefixMutation {
          prefixCreateUser(name: String): PrefixCreateUser
        }

        type PrefixCreateUser {
          name: String
        }

        type PrefixSubscription {
          prefixCountToTen: Int
        }
        """
        ).strip()
    )


def test_schema_object_type_name_prefix_camelcase_disabled():
    schema = Schema(
        Query,
        Mutation,
        Subscription,
        auto_camelcase=False,
        object_type_name_prefix="prefix",
    )
    assert (
        str(schema).strip()
        == dedent(
            """
        schema {
          query: PrefixQuery
          mutation: PrefixMutation
          subscription: PrefixSubscription
        }

        type PrefixQuery {
          prefix_inner: PrefixMyOtherType
        }

        type PrefixMyOtherType {
          field: String
          my_type: PrefixMyType
        }

        type PrefixMyType {
          field: String
        }

        type PrefixMutation {
          prefix_create_user(name: String): PrefixCreateUser
        }

        type PrefixCreateUser {
          name: String
        }

        type PrefixSubscription {
          prefix_count_to_ten: Int
        }
        """
        ).strip()
    )
