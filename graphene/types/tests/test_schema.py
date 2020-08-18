from graphql.type import GraphQLObjectType, GraphQLSchema
from graphql import GraphQLError
from pytest import raises, fixture

from graphene.tests.utils import dedent

from ..field import Field
from ..objecttype import ObjectType
from ..scalars import String
from ..schema import Schema, UnforgivingExecutionContext


class MyOtherType(ObjectType):
    field = String()


class Query(ObjectType):
    inner = Field(MyOtherType)


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
    assert str(schema) == dedent(
        """
        type Query {
          inner: MyOtherType
        }

        type MyOtherType {
          field: String
        }
        """
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


class TestUnforgivingExecutionContext:
    @fixture
    def schema(self):
        class MyQuery(ObjectType):
            sanity_field = String()
            expected_error_field = String()
            unexpected_error_field = String()

            @staticmethod
            def resolve_sanity_field(obj, info):
                return "not an error"

            @staticmethod
            def resolve_expected_error_field(obj, info):
                raise GraphQLError("expected error")

            @staticmethod
            def resolve_unexpected_error_field(obj, info):
                raise ValueError("unexpected error")

        schema = Schema(query=MyQuery)
        return schema

    def test_sanity_check(self, schema):
        # this should pass with no errors (sanity check)
        result = schema.execute(
            "query { sanityField }",
            execution_context_class=UnforgivingExecutionContext,
        )
        assert not result.errors
        assert result.data == {"sanityField": "not an error"}

    def test_graphql_error(self, schema):
        result = schema.execute(
            "query { expectedErrorField }",
            execution_context_class=UnforgivingExecutionContext,
        )
        assert len(result.errors) == 1
        assert result.errors[0].message == "expected error"
        assert result.data == {"expectedErrorField": None}

    def test_unexpected_error(self, schema):
        with raises(ValueError):
            # no result, but the exception should be propagated
            schema.execute(
                "query { unexpectedErrorField }",
                execution_context_class=UnforgivingExecutionContext,
            )
