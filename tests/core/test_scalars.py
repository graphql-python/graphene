from graphene.core.scalars import (
    GraphQLSkipField
)


def test_skipfield_serialize():
    f = GraphQLSkipField
    assert f.serialize('a') is None


def test_skipfield_parse_value():
    f = GraphQLSkipField
    assert f.parse_value('a') is None


def test_skipfield_parse_literal():
    f = GraphQLSkipField
    assert f.parse_literal('a') is None
