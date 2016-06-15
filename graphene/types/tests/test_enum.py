from graphql.type import GraphQLEnumType, GraphQLEnumValue

from ...utils.enum import Enum as PyEnum
from ..argument import Argument
from ..enum import Enum
from ..field import Field


def test_enum_construction():
    class RGB(Enum):
        RED = 1
        GREEN = 2
        BLUE = 3

    assert isinstance(RGB._meta.graphql_type, GraphQLEnumType)
    values = RGB._meta.graphql_type.get_values()
    assert values == [
        GraphQLEnumValue(name='RED', value=1),
        GraphQLEnumValue(name='GREEN', value=2),
        GraphQLEnumValue(name='BLUE', value=3),
    ]
    assert isinstance(RGB(name='field_name').as_field(), Field)
    assert isinstance(RGB(name='field_name').as_argument(), Argument)


def test_enum_instance_construction():
    RGB = Enum('RGB', 'RED,GREEN,BLUE')

    assert isinstance(RGB._meta.graphql_type, GraphQLEnumType)
    values = RGB._meta.graphql_type.get_values()
    assert values == [
        GraphQLEnumValue(name='RED', value=1),
        GraphQLEnumValue(name='GREEN', value=2),
        GraphQLEnumValue(name='BLUE', value=3),
    ]
    assert isinstance(RGB(name='field_name').as_field(), Field)
    assert isinstance(RGB(name='field_name').as_argument(), Argument)


def test_enum_from_builtin_enum():
    PyRGB = PyEnum('RGB', 'RED,GREEN,BLUE')

    RGB = Enum.from_enum(PyRGB)
    assert isinstance(RGB._meta.graphql_type, GraphQLEnumType)
    values = RGB._meta.graphql_type.get_values()
    assert values == [
        GraphQLEnumValue(name='RED', value=1),
        GraphQLEnumValue(name='GREEN', value=2),
        GraphQLEnumValue(name='BLUE', value=3),
    ]
    assert isinstance(RGB(name='field_name').as_field(), Field)
    assert isinstance(RGB(name='field_name').as_argument(), Argument)


def test_enum_value_from_class():
    class RGB(Enum):
        RED = 1
        GREEN = 2
        BLUE = 3

    assert RGB.RED.value == 1
