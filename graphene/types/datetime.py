from __future__ import absolute_import

import datetime

from aniso8601 import parse_date, parse_datetime, parse_time
from graphql.error import GraphQLError
from graphql.language import StringValueNode, print_ast

from .scalars import Scalar


class Date(Scalar):
    """
    The `Date` scalar type represents a Date
    value as specified by
    [iso8601](https://en.wikipedia.org/wiki/ISO_8601).
    """

    @staticmethod
    def serialize(date):
        if isinstance(date, datetime.datetime):
            date = date.date()
        if not isinstance(date, datetime.date):
            raise GraphQLError("Date cannot represent value: {}".format(repr(date)))
        return date.isoformat()

    @classmethod
    def parse_literal(cls, node):
        if not isinstance(node, StringValueNode):
            raise GraphQLError(
                "Date cannot represent non-string value: {}".format(print_ast(node))
            )
        return cls.parse_value(node.value)

    @staticmethod
    def parse_value(value):
        if isinstance(value, datetime.date):
            return value
        if not isinstance(value, str):
            raise GraphQLError(
                "Date cannot represent non-string value: {}".format(repr(value))
            )
        try:
            return parse_date(value)
        except ValueError:
            raise GraphQLError("Date cannot represent value: {}".format(repr(value)))


class DateTime(Scalar):
    """
    The `DateTime` scalar type represents a DateTime
    value as specified by
    [iso8601](https://en.wikipedia.org/wiki/ISO_8601).
    """

    @staticmethod
    def serialize(dt):
        if not isinstance(dt, (datetime.datetime, datetime.date)):
            raise GraphQLError("DateTime cannot represent value: {}".format(repr(dt)))
        return dt.isoformat()

    @classmethod
    def parse_literal(cls, node):
        if not isinstance(node, StringValueNode):
            raise GraphQLError(
                "DateTime cannot represent non-string value: {}".format(print_ast(node))
            )
        return cls.parse_value(node.value)

    @staticmethod
    def parse_value(value):
        if isinstance(value, datetime.datetime):
            return value
        if not isinstance(value, str):
            raise GraphQLError(
                "DateTime cannot represent non-string value: {}".format(repr(value))
            )
        try:
            return parse_datetime(value)
        except ValueError:
            raise GraphQLError(
                "DateTime cannot represent value: {}".format(repr(value))
            )


class Time(Scalar):
    """
    The `Time` scalar type represents a Time value as
    specified by
    [iso8601](https://en.wikipedia.org/wiki/ISO_8601).
    """

    @staticmethod
    def serialize(time):
        if not isinstance(time, datetime.time):
            raise GraphQLError("Time cannot represent value: {}".format(repr(time)))
        return time.isoformat()

    @classmethod
    def parse_literal(cls, node):
        if not isinstance(node, StringValueNode):
            raise GraphQLError(
                "Time cannot represent non-string value: {}".format(print_ast(node))
            )
        return cls.parse_value(node.value)

    @classmethod
    def parse_value(cls, value):
        if isinstance(value, datetime.time):
            return value
        if not isinstance(value, str):
            raise GraphQLError(
                "Time cannot represent non-string value: {}".format(repr(value))
            )
        try:
            return parse_time(value)
        except ValueError:
            raise GraphQLError("Time cannot represent value: {}".format(repr(value)))
