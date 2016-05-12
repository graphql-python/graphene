from graphql.type import GraphQLScalarType

from ...schema import Schema
from ..scalar import Scalar


def test_custom_scalar():
    import datetime
    from graphql.language import ast

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

    schema = Schema()

    scalar_type = schema.T(DateTimeScalar)
    assert isinstance(scalar_type, GraphQLScalarType)
    assert scalar_type.name == 'DateTimeScalar'
    assert scalar_type.description == 'DateTimeScalar Documentation'
