import pytest
import copy

from graphql import GraphQLString, GraphQLField, GraphQLInt, GraphQLNonNull

from ..field import Field
from ..argument import Argument
from ..objecttype import ObjectType
from ..scalars import String, Int


def test_field():
    field = Field(GraphQLString, name="name", description="description")
    assert isinstance(field, GraphQLField)
    assert field.name == "name"
    assert field.description == "description"
    assert field.type == GraphQLString


def test_field_required():
    field = Field(GraphQLString, required=True)
    assert isinstance(field, GraphQLField)
    assert isinstance(field.type, GraphQLNonNull)
    assert field.type.of_type == GraphQLString


def test_field_wrong_name():
    with pytest.raises(AssertionError) as excinfo:
        Field(GraphQLString, name="a field")

    assert """Names must match /^[_a-zA-Z][_a-zA-Z0-9]*$/ but "a field" does not.""" == str(excinfo.value)


def test_not_source_and_resolver():
    with pytest.raises(AssertionError) as excinfo:
        Field(GraphQLString, source="a", resolver=lambda *_:None)

    assert "You cannot have a source and a resolver at the same time" == str(excinfo.value)


def test_contributed_field_objecttype():
    class MyObject(ObjectType):
        pass

    field = Field(GraphQLString)
    field.contribute_to_class(MyObject, 'field_name')

    assert field.name == 'fieldName'


def test_contributed_field_non_objecttype():
    class MyObject(object):
        pass

    field = Field(GraphQLString)
    with pytest.raises(AssertionError):
        field.contribute_to_class(MyObject, 'field_name')


def test_copy_field_works():
    field = Field(GraphQLString)
    copy.copy(field)


def test_field_callable_type():
    field = Field(lambda: GraphQLString)
    assert field.type == GraphQLString


def test_field_with_arguments():
    field = Field(GraphQLString, name="name", description="description", input=Argument(GraphQLString))
    assert isinstance(field, GraphQLField)
    assert field.name == "name"
    assert field.description == "description"
    assert 'input' in field.args
    assert field.args['input'].type == GraphQLString


def test_field_with_argument_proxies():
    field = Field(GraphQLString, name="name", description="description", int=Int(), string=String())
    assert isinstance(field, GraphQLField)
    assert field.name == "name"
    assert field.description == "description"
    assert list(field.args.keys()) == ['int', 'string']
    assert field.args['string'].type == GraphQLString
    assert field.args['int'].type == GraphQLInt
