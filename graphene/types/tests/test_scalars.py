import datetime

import pytest

from graphene.utils.get_graphql_type import get_graphql_type
from graphql import graphql
from graphql.language import ast
from graphql.type import (GraphQLBoolean, GraphQLFieldDefinition, GraphQLFloat,
                          GraphQLInt, GraphQLScalarType, GraphQLString)

from ..field import Field
from ..objecttype import ObjectType
from ..scalars import Boolean, Float, Int, Scalar, String
from ..schema import Schema


class DatetimeScalar(Scalar):

    class Meta:
        name = 'DateTime'

    @staticmethod
    def serialize(dt):
        assert isinstance(dt, datetime.datetime)
        return dt.isoformat()

    @staticmethod
    def parse_literal(node):
        if isinstance(node, ast.StringValue):
            return datetime.datetime.strptime(node.value, "%Y-%m-%dT%H:%M:%S.%f")

    @staticmethod
    def parse_value(value):
        return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")


def serialize_date_time(dt):
    assert isinstance(dt, datetime.datetime)
    return dt.isoformat()


def parse_literal(node):
    if isinstance(node, ast.StringValue):
        return datetime.datetime.strptime(node.value, "%Y-%m-%dT%H:%M:%S.%f")


def parse_value(value):
    return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")


GraphQLDateTimeType = GraphQLScalarType(
    name='DateTime',
    serialize=serialize_date_time,
    parse_literal=parse_literal,
    parse_value=parse_value
)


class DatetimeScalarGraphQL(Scalar):

    class Meta:
        graphql_type = GraphQLDateTimeType


scalar_classes = {
    DatetimeScalar: DatetimeScalar._meta.graphql_type,
    DatetimeScalarGraphQL: GraphQLDateTimeType,
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
    assert list(fields.keys()) == ['before', 'field', 'after']
    assert isinstance(fields['field'], GraphQLFieldDefinition)


def test_custom_scalar_empty():
    with pytest.raises(AssertionError) as excinfo:
        class DatetimeScalar(Scalar):
            pass

    assert """DatetimeScalar must provide "serialize" function.""" in str(excinfo.value)


@pytest.mark.parametrize("scalar_class", (DatetimeScalar, DatetimeScalarGraphQL))
def test_custom_scalar_query(scalar_class):
    class Query(ObjectType):
        datetime = scalar_class(_in=scalar_class(name='in'))

        def resolve_datetime(self, args, context, info):
            return args.get('in')

    now = datetime.datetime.now()
    isoformat = now.isoformat()

    schema = Schema(query=Query)

    response = graphql(schema, '''
        {
            datetime(in: "%s")
        }
    ''' % isoformat)

    assert not response.errors
    assert response.data == {
        'datetime': isoformat
    }

    response = graphql(schema, '''
        query Test($date: DateTime) {
            datetime(in: $date)
        }
    ''', variable_values={
        'date': isoformat
    })

    assert not response.errors
    assert response.data == {
        'datetime': isoformat
    }
