import json

from graphql.core.language import ast
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
