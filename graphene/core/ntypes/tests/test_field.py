from graphql.core.type import GraphQLField, GraphQLInputObjectField, GraphQLString

from ..field import Field, InputField
from ..scalars import String
from graphene.core.types import ObjectType, InputObjectType
from graphene.core.schema import Schema


def test_field_internal_type():
    resolver = lambda *args: args

    field = Field(String, description='My argument', resolver=resolver)

    class Query(ObjectType):
        my_field = field
    schema = Schema(query=Query)

    type = schema.T(field)
    assert field.name == 'myField'
    assert isinstance(type, GraphQLField)
    assert type.description == 'My argument'
    assert type.resolver == resolver
    assert type.type == GraphQLString


def test_field_custom_name():
    field = Field(None, name='my_customName')

    class MyObjectType(ObjectType):
        my_field = field

    assert field.name == 'my_customName'


def test_field_custom_arguments():
    field = Field(None, name='my_customName', p=String())

    class MyObjectType(ObjectType):
        my_field = field

    schema = Schema(query=MyObjectType)

    args = field.get_arguments(schema)
    assert 'p' in args


def test_inputfield_internal_type():
    field = InputField(String, description='My input field', default='3')

    class MyObjectType(InputObjectType):
        my_field = field

    class Query(ObjectType):
        input_ot = Field(MyObjectType)

    schema = Schema(query=MyObjectType)

    type = schema.T(field)
    assert field.name == 'myField'
    assert isinstance(type, GraphQLInputObjectField)
    assert type.description == 'My input field'
    assert type.default_value == '3'
