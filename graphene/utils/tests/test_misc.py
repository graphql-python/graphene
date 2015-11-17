import collections

from graphql.core.type import GraphQLEnumType

from ..misc import enum_to_graphql_enum

item = collections.namedtuple('type', 'name value')


class MyCustomEnum(list):
    __name__ = 'MyName'


def test_enum_to_graphql_enum():
    assert isinstance(enum_to_graphql_enum(
        MyCustomEnum([item('k', 'v')])), GraphQLEnumType)
