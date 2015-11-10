from pytest import raises
from graphql.core.type import GraphQLArgument

from ..argument import Argument, to_arguments
from ..scalars import String
from graphene.core.types import ObjectType
from graphene.core.schema import Schema


def test_argument_internal_type():
    class MyObjectType(ObjectType):
        pass
    schema = Schema(query=MyObjectType)
    a = Argument(MyObjectType, description='My argument', default='3')
    type = schema.T(a)
    assert isinstance(type, GraphQLArgument)
    assert type.description == 'My argument'
    assert type.default_value == '3'


def test_to_arguments():
    arguments = to_arguments(
        Argument(String, name='myArg'),
        String(name='otherArg'),
        my_kwarg=String(),
        other_kwarg=String(),
    )

    assert [a.name for a in arguments] == ['myArg', 'otherArg', 'myKwarg', 'otherKwarg']


def test_to_arguments_no_name():
    with raises(AssertionError) as excinfo:
        to_arguments(
            String(),
        )
    assert 'must have a name' in str(excinfo.value)


def test_to_arguments_wrong_type():
    with raises(ValueError) as excinfo:
        to_arguments(
            p=3
        )
    assert 'Unknown argument p=3' == str(excinfo.value)
