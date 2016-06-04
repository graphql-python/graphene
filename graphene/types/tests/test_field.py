import pytest
import copy

from graphql import GraphQLString, GraphQLField

from ..field import Field
from ..objecttype import ObjectType


def test_field():
    field = Field(GraphQLString, name="name", description="description")
    assert isinstance(field, GraphQLField)
    assert field.name == "name"
    assert field.description == "description"


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

    assert field.name == 'field_name'


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
