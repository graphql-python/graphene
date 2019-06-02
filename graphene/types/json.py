from __future__ import absolute_import

import json

from graphql.language.ast import StringValueNode

from .scalars import Scalar


class JSONString(Scalar):
    """JSON String"""

    @staticmethod
    def serialize(dt):
        return json.dumps(dt)

    @staticmethod
    def parse_literal(node):
        if isinstance(node, StringValueNode):
            return json.loads(node.value)

    @staticmethod
    def parse_value(value):
        return json.loads(value)
