from textwrap import dedent

import pytest
from graphql import parse, build_ast_schema
from graphql.type import (
    GraphQLArgument,
    GraphQLEnumType,
    GraphQLEnumValue,
    GraphQLField,
    GraphQLInputField,
    GraphQLInputObjectType,
    GraphQLInterfaceType,
    GraphQLObjectType,
    GraphQLString,
)

from ..dynamic import Dynamic
from ..enum import Enum
from ..field import Field
from ..inputfield import InputField
from ..inputobjecttype import InputObjectType
from ..interface import Interface
from ..objecttype import ObjectType
from ..scalars import Int, String
from ..structures import List, NonNull
from ..schema import Schema
from ..union import Union


def create_type_map(types, auto_camelcase=True):
    query = type("Query", (ObjectType,), {})
    schema = Schema(query, types=types, auto_camelcase=auto_camelcase)
    return schema.graphql_schema.type_map


def test_enum():
    class MyEnum(Enum):
        """Description"""

        foo = 1
        bar = 2

        @property
        def description(self):
            return f"Description {self.name}={self.value}"

        @property
        def deprecation_reason(self):
            if self == MyEnum.foo:
                return "Is deprecated"

    type_map = create_type_map([MyEnum])
    assert "MyEnum" in type_map
    graphql_enum = type_map["MyEnum"]
    assert isinstance(graphql_enum, GraphQLEnumType)
    assert graphql_enum.name == "MyEnum"
    assert graphql_enum.description == "Description"
    assert graphql_enum.values == {
        "foo": GraphQLEnumValue(
            value=1, description="Description foo=1", deprecation_reason="Is deprecated"
        ),
        "bar": GraphQLEnumValue(value=2, description="Description bar=2"),
    }


def test_objecttype():
    class MyObjectType(ObjectType):
        """Description"""

        foo = String(
            bar=String(description="Argument description", default_value="x"),
            description="Field description",
        )
        bar = String(name="gizmo")

        def resolve_foo(self, bar):
            return bar

    type_map = create_type_map([MyObjectType])
    assert "MyObjectType" in type_map
    graphql_type = type_map["MyObjectType"]
    assert isinstance(graphql_type, GraphQLObjectType)
    assert graphql_type.name == "MyObjectType"
    assert graphql_type.description == "Description"

    fields = graphql_type.fields
    assert list(fields) == ["foo", "gizmo"]
    foo_field = fields["foo"]
    assert isinstance(foo_field, GraphQLField)
    assert foo_field.description == "Field description"

    assert foo_field.args == {
        "bar": GraphQLArgument(
            GraphQLString,
            description="Argument description",
            default_value="x",
            out_name="bar",
        )
    }


def test_dynamic_objecttype():
    class MyObjectType(ObjectType):
        """Description"""

        bar = Dynamic(lambda: Field(String))
        own = Field(lambda: MyObjectType)

    type_map = create_type_map([MyObjectType])
    assert "MyObjectType" in type_map
    assert list(MyObjectType._meta.fields) == ["bar", "own"]
    graphql_type = type_map["MyObjectType"]

    fields = graphql_type.fields
    assert list(fields) == ["bar", "own"]
    assert fields["bar"].type == GraphQLString
    assert fields["own"].type == graphql_type


def test_interface():
    class MyInterface(Interface):
        """Description"""

        foo = String(
            bar=String(description="Argument description", default_value="x"),
            description="Field description",
        )
        bar = String(name="gizmo", first_arg=String(), other_arg=String(name="oth_arg"))
        own = Field(lambda: MyInterface)

        def resolve_foo(self, args, info):
            return args.get("bar")

    type_map = create_type_map([MyInterface])
    assert "MyInterface" in type_map
    graphql_type = type_map["MyInterface"]
    assert isinstance(graphql_type, GraphQLInterfaceType)
    assert graphql_type.name == "MyInterface"
    assert graphql_type.description == "Description"

    fields = graphql_type.fields
    assert list(fields) == ["foo", "gizmo", "own"]
    assert fields["own"].type == graphql_type
    assert list(fields["gizmo"].args) == ["firstArg", "oth_arg"]
    foo_field = fields["foo"]
    assert isinstance(foo_field, GraphQLField)
    assert foo_field.description == "Field description"
    assert not foo_field.resolve  # Resolver not attached in interfaces
    assert foo_field.args == {
        "bar": GraphQLArgument(
            GraphQLString,
            description="Argument description",
            default_value="x",
            out_name="bar",
        )
    }


def test_inputobject():
    class OtherObjectType(InputObjectType):
        thingy = NonNull(Int)

    class MyInnerObjectType(InputObjectType):
        some_field = String()
        some_other_field = List(OtherObjectType)

    class MyInputObjectType(InputObjectType):
        """Description"""

        foo_bar = String(description="Field description")
        bar = String(name="gizmo")
        baz = NonNull(MyInnerObjectType)
        own = InputField(lambda: MyInputObjectType)

        def resolve_foo_bar(self, args, info):
            return args.get("bar")

    type_map = create_type_map([MyInputObjectType])
    assert "MyInputObjectType" in type_map
    graphql_type = type_map["MyInputObjectType"]
    assert isinstance(graphql_type, GraphQLInputObjectType)
    assert graphql_type.name == "MyInputObjectType"
    assert graphql_type.description == "Description"

    other_graphql_type = type_map["OtherObjectType"]
    inner_graphql_type = type_map["MyInnerObjectType"]
    container = graphql_type.out_type(
        {
            "bar": "oh!",
            "baz": inner_graphql_type.out_type(
                {
                    "some_other_field": [
                        other_graphql_type.out_type({"thingy": 1}),
                        other_graphql_type.out_type({"thingy": 2}),
                    ]
                }
            ),
        }
    )
    assert isinstance(container, MyInputObjectType)
    assert "bar" in container
    assert container.bar == "oh!"
    assert "foo_bar" not in container
    assert container.foo_bar is None
    assert container.baz.some_field is None
    assert container.baz.some_other_field[0].thingy == 1
    assert container.baz.some_other_field[1].thingy == 2

    fields = graphql_type.fields
    assert list(fields) == ["fooBar", "gizmo", "baz", "own"]
    own_field = fields["own"]
    assert own_field.type == graphql_type
    foo_field = fields["fooBar"]
    assert isinstance(foo_field, GraphQLInputField)
    assert foo_field.description == "Field description"


def test_objecttype_camelcase():
    class MyObjectType(ObjectType):
        """Description"""

        foo_bar = String(bar_foo=String())

    type_map = create_type_map([MyObjectType])
    assert "MyObjectType" in type_map
    graphql_type = type_map["MyObjectType"]
    assert isinstance(graphql_type, GraphQLObjectType)
    assert graphql_type.name == "MyObjectType"
    assert graphql_type.description == "Description"

    fields = graphql_type.fields
    assert list(fields) == ["fooBar"]
    foo_field = fields["fooBar"]
    assert isinstance(foo_field, GraphQLField)
    assert foo_field.args == {
        "barFoo": GraphQLArgument(GraphQLString, default_value=None, out_name="bar_foo")
    }


def test_objecttype_camelcase_disabled():
    class MyObjectType(ObjectType):
        """Description"""

        foo_bar = String(bar_foo=String())

    type_map = create_type_map([MyObjectType], auto_camelcase=False)
    assert "MyObjectType" in type_map
    graphql_type = type_map["MyObjectType"]
    assert isinstance(graphql_type, GraphQLObjectType)
    assert graphql_type.name == "MyObjectType"
    assert graphql_type.description == "Description"

    fields = graphql_type.fields
    assert list(fields) == ["foo_bar"]
    foo_field = fields["foo_bar"]
    assert isinstance(foo_field, GraphQLField)
    assert foo_field.args == {
        "bar_foo": GraphQLArgument(
            GraphQLString, default_value=None, out_name="bar_foo"
        )
    }


def test_objecttype_with_possible_types():
    class MyObjectType(ObjectType):
        """Description"""

        class Meta:
            possible_types = (dict,)

        foo_bar = String()

    type_map = create_type_map([MyObjectType])
    graphql_type = type_map["MyObjectType"]
    assert graphql_type.is_type_of
    assert graphql_type.is_type_of({}, None) is True
    assert graphql_type.is_type_of(MyObjectType(), None) is False


def test_graphql_type():
    """Type map should allow direct GraphQL types"""
    MyGraphQLType = GraphQLObjectType(
        name="MyGraphQLType",
        fields={
            "hello": GraphQLField(GraphQLString, resolve=lambda obj, info: "world")
        },
    )

    class Query(ObjectType):
        graphql_type = Field(MyGraphQLType)

        def resolve_graphql_type(root, info):
            return {}

    schema = Schema(query=Query)
    assert str(schema) == dedent(
        """\
        type Query {
          graphqlType: MyGraphQLType
        }

        type MyGraphQLType {
          hello: String
        }
    """
    )

    results = schema.execute(
        """
        query {
            graphqlType {
                hello
            }
        }
    """
    )
    assert not results.errors
    assert results.data == {"graphqlType": {"hello": "world"}}


def test_graphql_type_interface():
    MyGraphQLInterface = GraphQLInterfaceType(
        name="MyGraphQLType",
        fields={
            "hello": GraphQLField(GraphQLString, resolve=lambda obj, info: "world")
        },
    )

    with pytest.raises(AssertionError) as error:

        class MyGrapheneType(ObjectType):
            class Meta:
                interfaces = (MyGraphQLInterface,)

    assert str(error.value) == (
        "All interfaces of MyGrapheneType must be a subclass of Interface. "
        'Received "MyGraphQLType".'
    )


def test_graphql_type_union():
    MyGraphQLType = GraphQLObjectType(
        name="MyGraphQLType",
        fields={
            "hello": GraphQLField(GraphQLString, resolve=lambda obj, info: "world")
        },
    )

    class MyGrapheneType(ObjectType):
        hi = String(default_value="world")

    class MyUnion(Union):
        class Meta:
            types = (MyGraphQLType, MyGrapheneType)

        @classmethod
        def resolve_type(cls, instance, info):
            return MyGraphQLType

    class Query(ObjectType):
        my_union = Field(MyUnion)

        def resolve_my_union(root, info):
            return {}

    schema = Schema(query=Query)
    assert str(schema) == dedent(
        """\
        type Query {
          myUnion: MyUnion
        }

        union MyUnion = MyGraphQLType | MyGrapheneType

        type MyGraphQLType {
          hello: String
        }

        type MyGrapheneType {
          hi: String
        }
    """
    )

    results = schema.execute(
        """
        query {
            myUnion {
                __typename
            }
        }
    """
    )
    assert not results.errors
    assert results.data == {"myUnion": {"__typename": "MyGraphQLType"}}


def test_graphql_type_from_sdl():
    types = """
        type Pet {
            name: String!
        }

        type User {
            name: String!
            pets: [Pet!]!
        }
    """
    ast_document = parse(types)
    sdl_schema = build_ast_schema(ast_document)

    class Query(ObjectType):
        my_user = Field(sdl_schema.get_type("User"))

    schema = Schema(query=Query)
    assert str(schema) == dedent(
        """\
        type Query {
          myUser: User
        }

        type User {
          name: String!
          pets: [Pet!]!
        }

        type Pet {
          name: String!
        }
    """
    )
