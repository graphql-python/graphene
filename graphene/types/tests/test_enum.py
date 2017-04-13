from ..enum import Enum, PyEnum
from ..field import Field
from ..inputfield import InputField
from ..argument import Argument


def test_enum_construction():
    class RGB(Enum):
        '''Description'''
        RED = 1
        GREEN = 2
        BLUE = 3

        @property
        def description(self):
            return "Description {}".format(self.name)

    assert RGB._meta.name == 'RGB'
    assert RGB._meta.description == 'Description'

    values = RGB._meta.enum.__members__.values()
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


def test_enum_construction_meta():
    class RGB(Enum):

        class Meta:
            name = 'RGBEnum'
            description = 'Description'
        RED = 1
        GREEN = 2
        BLUE = 3

    assert RGB._meta.name == 'RGBEnum'
    assert RGB._meta.description == 'Description'


def test_enum_instance_construction():
    RGB = Enum('RGB', 'RED,GREEN,BLUE')

    values = RGB._meta.enum.__members__.values()
    assert sorted([v.name for v in values]) == [
        'BLUE',
        'GREEN',
        'RED'
    ]


def test_enum_from_builtin_enum():
    PyRGB = PyEnum('RGB', 'RED,GREEN,BLUE')

    RGB = Enum.from_enum(PyRGB)
    assert RGB._meta.enum == PyRGB
    assert RGB.RED
    assert RGB.GREEN
    assert RGB.BLUE


def test_enum_value_from_class():
    class RGB(Enum):
        RED = 1
        GREEN = 2
        BLUE = 3

    assert RGB.RED.value == 1
    assert RGB.GREEN.value == 2
    assert RGB.BLUE.value == 3


def test_enum_value_as_unmounted_field():
    class RGB(Enum):
        RED = 1
        GREEN = 2
        BLUE = 3

    unmounted = RGB()
    unmounted_field = unmounted.Field()
    assert isinstance(unmounted_field, Field)
    assert unmounted_field.type == RGB


def test_enum_value_as_unmounted_inputfield():
    class RGB(Enum):
        RED = 1
        GREEN = 2
        BLUE = 3

    unmounted = RGB()
    unmounted_field = unmounted.InputField()
    assert isinstance(unmounted_field, InputField)
    assert unmounted_field.type == RGB


def test_enum_value_as_unmounted_argument():
    class RGB(Enum):
        RED = 1
        GREEN = 2
        BLUE = 3

    unmounted = RGB()
    unmounted_field = unmounted.Argument()
    assert isinstance(unmounted_field, Argument)
    assert unmounted_field.type == RGB


def test_enum_can_be_compared():
    class RGB(Enum):
        RED = 1
        GREEN = 2
        BLUE = 3

    assert RGB.RED == 1
    assert RGB.GREEN == 2
    assert RGB.BLUE == 3


def test_enum_can_be_initialzied():
    class RGB(Enum):
        RED = 1
        GREEN = 2
        BLUE = 3

    assert RGB.get(1) == RGB.RED
    assert RGB.get(2) == RGB.GREEN
    assert RGB.get(3) == RGB.BLUE


def test_enum_can_retrieve_members():
    class RGB(Enum):
        RED = 1
        GREEN = 2
        BLUE = 3

    assert RGB['RED'] == RGB.RED
    assert RGB['GREEN'] == RGB.GREEN
    assert RGB['BLUE'] == RGB.BLUE


def test_enum_to_enum_comparison_should_differ():
    class RGB1(Enum):
        RED = 1
        GREEN = 2
        BLUE = 3

    class RGB2(Enum):
        RED = 1
        GREEN = 2
        BLUE = 3

    assert RGB1.RED != RGB2.RED
    assert RGB1.GREEN != RGB2.GREEN
    assert RGB1.BLUE != RGB2.BLUE
