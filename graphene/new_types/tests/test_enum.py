from ..enum import Enum, PyEnum


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
