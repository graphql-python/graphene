from graphql.core.type import GraphQLList, GraphQLNonNull, GraphQLString

from graphene.core.schema import Schema

from ..definitions import List, NonNull
from ..scalars import String

schema = Schema()


def test_list_scalar():
    type = schema.T(List(String()))
    assert isinstance(type, GraphQLList)
    assert type.of_type == GraphQLString


def test_nonnull_scalar():
    type = schema.T(NonNull(String()))
    assert isinstance(type, GraphQLNonNull)
    assert type.of_type == GraphQLString


def test_nested_scalars():
    type = schema.T(NonNull(List(String())))
    assert isinstance(type, GraphQLNonNull)
    assert isinstance(type.of_type, GraphQLList)
    assert type.of_type.of_type == GraphQLString
