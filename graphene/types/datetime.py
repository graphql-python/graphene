from __future__ import absolute_import

import datetime
try:
    import iso8601
except:
    raise ImportError("iso8601 package is required for DateTime Scalar.\nYou can install it using: pip install iso8601.")
from graphql.language import ast

from .scalars import Scalar


class DateTime(Scalar):

    @staticmethod
    def serialize(dt):
        assert isinstance(dt, datetime.datetime)
        return dt.isoformat()

    @staticmethod
    def parse_literal(node):
        if isinstance(node, ast.StringValue):
            return iso8601.parse_date(node.value)

    @staticmethod
    def parse_value(value):
        return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")
