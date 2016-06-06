import pytest
import copy

from graphql import GraphQLString, GraphQLArgument

from ..argument import Argument, to_arguments
from ..scalars import String


def test_argument():
    argument = Argument(GraphQLString, name="name", description="description")
    assert isinstance(argument, GraphQLArgument)
    assert argument.name == "name"
    assert argument.description == "description"
    assert argument.type == GraphQLString


def test_field_wrong_name():
    with pytest.raises(AssertionError) as excinfo:
        Argument(GraphQLString, name="a field")

    assert """Names must match /^[_a-zA-Z][_a-zA-Z0-9]*$/ but "a field" does not.""" == str(excinfo.value)


def test_argument_type():
    argument = Argument(lambda: GraphQLString)
    assert argument.type == GraphQLString


def test_argument_graphene_type():
    argument = Argument(String)
    assert argument.type == GraphQLString


def test_argument_proxy_graphene_type():
    proxy = String()
    argument = proxy.as_argument()
    assert argument.type == GraphQLString


def test_copy_argument_works():
    argument = Argument(GraphQLString)
    copy.copy(argument)


def test_to_arguments():
    arguments = to_arguments(a=String(), b=Argument(GraphQLString), c=Argument(String))
    assert list(arguments.keys()) == ['a', 'b', 'c']
    assert [a.type for a in arguments.values()] == [GraphQLString] * 3


def test_to_arguments_incorrect():
    with pytest.raises(ValueError) as excinfo:
        to_arguments(incorrect=object())

    assert """Unknown argument "incorrect".""" == str(excinfo.value)


def test_to_arguments_no_name():
    with pytest.raises(AssertionError) as excinfo:
        to_arguments(dict(a=String()), dict(a=String()))

    assert """More than one Argument have same name "a".""" == str(excinfo.value)
