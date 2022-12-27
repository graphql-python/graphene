from textwrap import dedent

from ..field import Field
from ..enum import Enum
from ..inputobjecttype import InputObjectType
from ..interface import Interface
from ..mutation import Mutation as Mutation_
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
    my_scalar = MyScalar()
    my_enum = MyEnum()


class MyFooType(ObjectType):
    field = String()


class MyUnion(Union):
    class Meta:
        types = (MyBarType, MyFooType)


class MyType(ObjectType):
    field = String()
    my_union = MyUnion()
    my_bar_type = Field(MyBarType)


class Query(ObjectType):
    inner = Field(MyType)


class CreateUser(Mutation_):
    class Arguments:
        name = String()

    name = String()

    def mutate(self, info, name):
        return CreateUser(name=name)


class Mutation(ObjectType):
    create_user = CreateUser.Field()


class Subscription(ObjectType):
    count_to_ten = Field(Int)


def test_schema_type_name_prefix_camelcase():

    schema = Schema(
        Query,
        Mutation,
        Subscription,
        auto_camelcase=True,
        type_name_prefix="MyPrefix",
    )
    assert (
        str(schema).strip()
        == dedent(
            """
        type Query {
          myPrefixInner: MyPrefixMyType
        }

        type MyPrefixMyType {
          field: String
          myUnion: MyPrefixMyUnion
          myBarType: MyPrefixMyBarType
        }

        union MyPrefixMyUnion = MyPrefixMyBarType | MyPrefixMyFooType

        type MyPrefixMyBarType {
          field(input: MyPrefixMyInputObjectType): String
          myInterface: MyPrefixMyInterface
          myScalar: MyPrefixMyScalar
          myEnum: MyPrefixMyEnum
        }

        input MyPrefixMyInputObjectType {
          field: String
        }

        interface MyPrefixMyInterface {
          field: String
        }

        scalar MyPrefixMyScalar

        enum MyPrefixMyEnum {
          FOO
          BAR
        }

        type MyPrefixMyFooType {
          field: String
        }

        type Mutation {
          myPrefixCreateUser(name: String): MyPrefixCreateUser
        }

        type MyPrefixCreateUser {
          name: String
        }

        type Subscription {
          myPrefixCountToTen: Int
        }
        """
        ).strip()
    )


def test_schema_type_name_prefix_camelcase_disabled():
    schema = Schema(
        Query,
        Mutation,
        Subscription,
        auto_camelcase=False,
        type_name_prefix="MyPrefix",
    )
    assert (
        str(schema).strip()
        == dedent(
            """
        type Query {
          MyPrefixinner: MyPrefixMyType
        }

        type MyPrefixMyType {
          field: String
          my_union: MyPrefixMyUnion
          my_bar_type: MyPrefixMyBarType
        }

        union MyPrefixMyUnion = MyPrefixMyBarType | MyPrefixMyFooType

        type MyPrefixMyBarType {
          field(input: MyPrefixMyInputObjectType): String
          my_interface: MyPrefixMyInterface
          my_scalar: MyPrefixMyScalar
          my_enum: MyPrefixMyEnum
        }

        input MyPrefixMyInputObjectType {
          field: String
        }

        interface MyPrefixMyInterface {
          field: String
        }

        scalar MyPrefixMyScalar

        enum MyPrefixMyEnum {
          FOO
          BAR
        }

        type MyPrefixMyFooType {
          field: String
        }

        type Mutation {
          MyPrefixcreate_user(name: String): MyPrefixCreateUser
        }

        type MyPrefixCreateUser {
          name: String
        }

        type Subscription {
          MyPrefixcount_to_ten: Int
        }
        """
        ).strip()
    )


def test_schema_type_name_prefix_override():
    class MyInputObjectType(InputObjectType):
        class Meta:
            type_name_prefix = "OverridePrefix"

        field = String()

    class MyScalar(Scalar):
        class Meta:
            type_name_prefix = ""

    class MyEnum(Enum):
        class Meta:
            type_name_prefix = ""

        FOO = "foo"
        BAR = "bar"

    class MyInterface(Interface):
        class Meta:
            type_name_prefix = ""

        field = String()

    class MyBarType(ObjectType):
        class Meta:
            type_name_prefix = ""

        field = String(input=MyInputObjectType())
        my_interface = Field(MyInterface)
        my_scalar = MyScalar()
        my_enum = MyEnum()

    class MyFooType(ObjectType):
        class Meta:
            type_name_prefix = ""

        field = String()

    class MyUnion(Union):
        class Meta:
            type_name_prefix = ""
            types = (MyBarType, MyFooType)

    class MyType(ObjectType):
        class Meta:
            type_name_prefix = ""

        field = String()
        my_union = MyUnion()
        my_bar_type = Field(MyBarType)

    class Query(ObjectType):
        class Meta:
            type_name_prefix = "OverridePrefix"

        inner = Field(MyType)

    class CreateUser(Mutation_):
        class Meta:
            type_name_prefix = ""

        class Arguments:
            name = String()

        name = String()

        def mutate(self, info, name):
            return CreateUser(name=name)

    class Mutation(ObjectType):
        class Meta:
            type_name_prefix = ""

        create_user = CreateUser.Field()

    class Subscription(ObjectType):
        class Meta:
            type_name_prefix = ""

        count_to_ten = Field(Int)

    schema = Schema(
        Query,
        Mutation,
        Subscription,
        auto_camelcase=True,
        type_name_prefix="MyPrefix",
    )
    assert (
        str(schema).strip()
        == dedent(
            """
        type Query {
          overridePrefixInner: MyType
        }

        type MyType {
          field: String
          myUnion: MyUnion
          myBarType: MyBarType
        }

        union MyUnion = MyBarType | MyFooType

        type MyBarType {
          field(input: OverridePrefixMyInputObjectType): String
          myInterface: MyInterface
          myScalar: MyScalar
          myEnum: MyEnum
        }

        input OverridePrefixMyInputObjectType {
          field: String
        }

        interface MyInterface {
          field: String
        }

        scalar MyScalar

        enum MyEnum {
          FOO
          BAR
        }

        type MyFooType {
          field: String
        }

        type Mutation {
          createUser(name: String): CreateUser
        }

        type CreateUser {
          name: String
        }

        type Subscription {
          countToTen: Int
        }
        """
        ).strip()
    )
