import json

import iso8601
from graphql.language import ast

from ...core.classtypes.scalar import Scalar


class JSONString(Scalar):
    '''JSON String'''

    @staticmethod
    def serialize(dt):
        return json.dumps(dt)

    @staticmethod
    def parse_literal(node):
        if isinstance(node, ast.StringValue):
            return json.dumps(node.value)

    @staticmethod
    def parse_value(value):
        return json.dumps(value)


class DateTime(Scalar):
    '''DateTime in ISO 8601 format'''

    @staticmethod
    def serialize(dt):
        return dt.isoformat()

    @staticmethod
    def parse_literal(node):
        if isinstance(node, ast.StringValue):
            return iso8601.parse_date(node.value)

    @staticmethod
    def parse_value(value):
        return iso8601.parse_date(value)
