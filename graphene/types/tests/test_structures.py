import pytest

from graphql import GraphQLString, GraphQLList, GraphQLNonNull

from ..structures import List, NonNull
from ..scalars import String
from ..field import Field


def test_list():
    list_instance = List(String)
    assert isinstance(list_instance, GraphQLList)
    assert list_instance.of_type == GraphQLString


def test_list_lambda():
    list_instance = List(lambda: String)
    assert isinstance(list_instance, GraphQLList)
    assert list_instance.of_type == GraphQLString


def test_list_list():
    list_instance = List(List(String))
    assert isinstance(list_instance, GraphQLList)
    assert isinstance(list_instance.of_type, GraphQLList)
    assert list_instance.of_type.of_type == GraphQLString


def test_nonnull():
    list_instance = NonNull(String)
    assert isinstance(list_instance, GraphQLNonNull)
    assert list_instance.of_type == GraphQLString


def test_nonnull_lambda():
    list_instance = NonNull(lambda: String)
    assert isinstance(list_instance, GraphQLNonNull)
    assert list_instance.of_type == GraphQLString


def test_nonnull_list():
    list_instance = NonNull(List(String))
    assert isinstance(list_instance, GraphQLNonNull)
    assert isinstance(list_instance.of_type, GraphQLList)
    assert list_instance.of_type.of_type == GraphQLString


def test_preserve_order():
    field1 = List(lambda: None)
    field2 = Field(lambda: None)

    assert field1 < field2
