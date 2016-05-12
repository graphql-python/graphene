from graphql.type import (GraphQLBoolean, GraphQLFloat, GraphQLID, GraphQLInt,
                          GraphQLString)

from graphene.core.schema import Schema

from ..scalars import ID, Boolean, Float, Int, String

schema = Schema()


def test_string_scalar():
    assert schema.T(String()) == GraphQLString


def test_int_scalar():
    assert schema.T(Int()) == GraphQLInt


def test_boolean_scalar():
    assert schema.T(Boolean()) == GraphQLBoolean


def test_id_scalar():
    assert schema.T(ID()) == GraphQLID


def test_float_scalar():
    assert schema.T(Float()) == GraphQLFloat
