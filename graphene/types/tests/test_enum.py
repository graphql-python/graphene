from graphql.type import GraphQLEnumType

from ..argument import Argument
from ..enum import Enum, PyEnum
from ..field import Field


def test_enum_construction():
    class RGB(Enum):
        RED = 1
        GREEN = 2
        BLUE = 3

        @property
        def description(self):
            return "Description {}".format(self.name)

    assert isinstance(RGB._meta.graphql_type, GraphQLEnumType)
    values = RGB._meta.graphql_type.get_values()
    assert sorted([v.name for v in values]) == [
        'BLUE',
        'GREEN',
        'RED'
    ]
    assert sorted([v.description for v in values]) == [
        'Description BLUE',
        'Description GREEN',
        'Description RED'
    ]
    assert isinstance(RGB(name='field_name').as_field(), Field)
    assert isinstance(RGB(name='field_name').as_argument(), Argument)


def test_enum_instance_construction():
    RGB = Enum('RGB', 'RED,GREEN,BLUE')

    assert isinstance(RGB._meta.graphql_type, GraphQLEnumType)
    values = RGB._meta.graphql_type.get_values()
    assert sorted([v.name for v in values]) == [
        'BLUE',
        'GREEN',
        'RED'
    ]
    assert isinstance(RGB(name='field_name').as_field(), Field)
    assert isinstance(RGB(name='field_name').as_argument(), Argument)


def test_enum_from_builtin_enum():
    PyRGB = PyEnum('RGB', 'RED,GREEN,BLUE')

    RGB = Enum.from_enum(PyRGB)
    assert isinstance(RGB._meta.graphql_type, GraphQLEnumType)
    values = RGB._meta.graphql_type.get_values()
    assert sorted([v.name for v in values]) == [
        'BLUE',
        'GREEN',
        'RED'
    ]
    assert isinstance(RGB(name='field_name').as_field(), Field)
    assert isinstance(RGB(name='field_name').as_argument(), Argument)


def test_enum_value_from_class():
    class RGB(Enum):
        RED = 1
        GREEN = 2
        BLUE = 3

    assert RGB.RED.value == 1
