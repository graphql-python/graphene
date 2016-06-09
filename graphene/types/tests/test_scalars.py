import pytest
from ..scalars import Scalar, String, Int, Float, Boolean
from ..field import Field
from ..objecttype import ObjectType

from graphql import GraphQLString, GraphQLInt, GraphQLFloat, GraphQLBoolean
from graphene.utils.get_graphql_type import get_graphql_type


class DatetimeScalar(Scalar):
    def serialize(value):
        return value.isoformat()


scalar_classes = {
    DatetimeScalar: DatetimeScalar._meta.graphql_type,
    String: GraphQLString,
    Int: GraphQLInt,
    Float: GraphQLFloat,
    Boolean: GraphQLBoolean,
}


@pytest.mark.parametrize("scalar_class,expected_graphql_type", scalar_classes.items())
def test_scalar_as_field(scalar_class, expected_graphql_type):
    field_before = Field(None)
    scalar = scalar_class()
    field = scalar.as_field()
    graphql_type = get_graphql_type(scalar_class)
    field_after = Field(None)
    assert isinstance(field, Field)
    assert field.type == graphql_type
    assert graphql_type == expected_graphql_type
    assert field_before < field < field_after


@pytest.mark.parametrize("scalar_class,graphql_type", scalar_classes.items())
def test_scalar_in_objecttype(scalar_class, graphql_type):
    class MyObjectType(ObjectType):
        before = Field(scalar_class)
        field = scalar_class()
        after = Field(scalar_class)

    graphql_type = get_graphql_type(MyObjectType)
    fields = graphql_type.get_fields()
    assert fields.keys() == ['before', 'field', 'after']
    assert isinstance(fields['field'], Field)


def test_custom_scalar_empty():
    with pytest.raises(AssertionError) as excinfo:
        class DatetimeScalar(Scalar):
            pass

    assert """DatetimeScalar must provide "serialize" function.""" in str(excinfo.value)
