from __future__ import absolute_import
import six
from uuid import UUID as _UUID

from graphql.language import ast

from .scalars import Scalar


class UUID(Scalar):
    """
    Leverages the internal Python implmeentation of UUID (uuid.UUID) to provide native UUID objects
    in fields, resolvers and input.
    """

    @staticmethod
    def serialize(uuid):
        if isinstance(uuid, six.string_types):
            uuid = _UUID(uuid)

        assert isinstance(uuid, _UUID), "Expected UUID instance, received {}".format(
            uuid
        )
        return str(uuid)

    @staticmethod
    def parse_literal(node):
        if isinstance(node, ast.StringValue):
            return _UUID(node.value)

    @staticmethod
    def parse_value(value):
        return _UUID(value)
