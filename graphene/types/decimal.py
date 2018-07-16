from __future__ import absolute_import

from decimal import Decimal as _Decimal

from graphql.language import ast

from .scalars import Scalar


class Decimal(Scalar):
    """
    The `Decimal` scalar type represents a python Decimal.
    """

    @staticmethod
    def serialize(dec):
        if isinstance(dec, str):
            dec = _Decimal(dec)
        assert isinstance(dec, _Decimal), 'Received not compatible Decimal "{}"'.format(
            repr(dec)
        )
        return str(dec)

    @classmethod
    def parse_literal(cls, node):
        if isinstance(node, ast.StringValue):
            return cls.parse_value(node.value)

    @staticmethod
    def parse_value(value):
        try:
            return _Decimal(value)
        except ValueError:
            return None
