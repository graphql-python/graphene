import collections

from graphene.utils.misc import enum_to_graphql_enum
from graphql.core.type import GraphQLEnumType

item = collections.namedtuple('type', 'name value')


class MyCustomEnum(list):
    __name__ = 'MyName'


def test_enum_to_graphql_enum():
    assert isinstance(enum_to_graphql_enum(
        MyCustomEnum([item('k', 'v')])), GraphQLEnumType)
