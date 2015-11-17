from mock import patch

from graphene.core.types import InputObjectType, ObjectType

from ..argument import Argument
from ..base import MountedType, OrderedType
from ..definitions import List, NonNull
from ..field import Field, InputField


def test_orderedtype_equal():
    a = OrderedType()
    assert a == a
    assert hash(a) == hash(a)


def test_orderedtype_different():
    a = OrderedType()
    b = OrderedType()
    assert a != b
    assert hash(a) != hash(b)
    assert a < b
    assert b > a


@patch('graphene.core.types.field.Field')
def test_type_as_field_called(Field):
    resolver = lambda x: x
    a = MountedType(2, description='A', resolver=resolver)
    a.as_field()
    Field.assert_called_with(
        a,
        2,
        _creation_counter=a.creation_counter,
        description='A',
        resolver=resolver)


@patch('graphene.core.types.argument.Argument')
def test_type_as_argument_called(Argument):
    a = MountedType(2, description='A')
    a.as_argument()
    Argument.assert_called_with(
        a, 2, _creation_counter=a.creation_counter, description='A')


def test_type_as_field():
    resolver = lambda x: x

    class MyObjectType(ObjectType):
        t = MountedType(description='A', resolver=resolver)

    fields_map = MyObjectType._meta.fields_map
    field = fields_map.get('t')
    assert isinstance(field, Field)
    assert field.description == 'A'
    assert field.object_type == MyObjectType


def test_type_as_inputfield():
    class MyObjectType(InputObjectType):
        t = MountedType(description='A')

    fields_map = MyObjectType._meta.fields_map
    field = fields_map.get('t')
    assert isinstance(field, InputField)
    assert field.description == 'A'
    assert field.object_type == MyObjectType


def test_type_as_argument():
    a = MountedType(description='A')
    argument = a.as_argument()
    assert isinstance(argument, Argument)


def test_type_as_list():
    m = MountedType(2, 3, my_c='A')
    a = m.List

    assert isinstance(a, List)
    assert a.of_type == m
    assert a.args == (2, 3)
    assert a.kwargs == {'my_c': 'A'}


def test_type_as_nonnull():
    m = MountedType(2, 3, my_c='A')
    a = m.NonNull

    assert isinstance(a, NonNull)
    assert a.of_type == m
    assert a.args == (2, 3)
    assert a.kwargs == {'my_c': 'A'}
