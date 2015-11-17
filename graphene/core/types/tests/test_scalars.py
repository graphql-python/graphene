from graphql.core.type import (GraphQLBoolean, GraphQLFloat, GraphQLID,
                               GraphQLInt, GraphQLScalarType, GraphQLString)

from graphene.core.schema import Schema

from ..scalars import ID, Boolean, Float, Int, Scalar, String

schema = Schema()


def test_string_scalar():
    assert schema.T(String()) == GraphQLString


def test_int_scalar():
    assert schema.T(Int()) == GraphQLInt


def test_boolean_scalar():
    assert schema.T(Boolean()) == GraphQLBoolean


def test_id_scalar():
    assert schema.T(ID()) == GraphQLID


def test_float_scalar():
    assert schema.T(Float()) == GraphQLFloat


def test_custom_scalar():
    import datetime
    from graphql.core.language import ast

    class DateTimeScalar(Scalar):
        '''DateTimeScalar Documentation'''
        @staticmethod
        def serialize(dt):
            return dt.isoformat()

        @staticmethod
        def parse_literal(node):
            if isinstance(node, ast.StringValue):
                return datetime.datetime.strptime(
                    node.value, "%Y-%m-%dT%H:%M:%S.%f")

        @staticmethod
        def parse_value(value):
            return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")

    scalar_type = schema.T(DateTimeScalar)
    assert isinstance(scalar_type, GraphQLScalarType)
    assert scalar_type.name == 'DateTimeScalar'
    assert scalar_type.description == 'DateTimeScalar Documentation'
