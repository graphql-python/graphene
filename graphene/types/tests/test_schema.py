from textwrap import dedent

from pytest import raises

from graphql.type import GraphQLObjectType, GraphQLSchema

from ..field import Field
from ..enum import Enum
from ..inputobjecttype import InputObjectType
from ..interface import Interface
from ..mutation import Mutation
from ..objecttype import ObjectType
from ..scalars import Int, String, Scalar
from ..schema import Schema
from ..union import Union


class MyInputObjectType(InputObjectType):
    field = String()


class MyScalar(Scalar):
    ...


class MyEnum(Enum):
    FOO = "foo"
    BAR = "bar"


class MyInterface(Interface):
    field = String()


class MyBarType(ObjectType):
    field = String(input=MyInputObjectType())
    my_interface = Field(MyInterface)


class MyFooType(ObjectType):
    field = String()
    my_scalar = MyScalar()
    my_enum = MyEnum()


class MyUnion(Union):
    class Meta:
        types = (MyBarType, MyFooType)


class MyType(ObjectType):
    field = String()
    my_union = MyUnion()
    my_bar_type = Field(MyBarType)
    my_foo_type = Field("graphene.types.tests.test_schema.MyFooType")


class Query(ObjectType):
    inner = Field(MyType)


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
    assert schema.MyType == MyType
    assert schema.MyBarType == MyBarType
    assert schema.MyFooType == MyFooType
    assert schema.MyInputObjectType == MyInputObjectType
    assert schema.MyInterface == MyInterface
    assert schema.MyEnum == MyEnum


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
          inner: MyType
        }

        type MyType {
          field: String
          myUnion: MyUnion
          myBarType: MyBarType
          myFooType: MyFooType
        }

        union MyUnion = MyBarType | MyFooType

        type MyBarType {
          field(input: MyInputObjectType): String
          myInterface: MyInterface
        }

        input MyInputObjectType {
          field: String
        }

        interface MyInterface {
          field: String
        }

        type MyFooType {
          field: String
          myScalar: MyScalar
          myEnum: MyEnum
        }

        scalar MyScalar

        enum MyEnum {
          FOO
          BAR
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
