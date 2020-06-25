from textwrap import dedent

from graphene.compat.middleware import enum_value_convertor_middleware
from ..argument import Argument
from ..enum import Enum, PyEnum
from ..field import Field
from ..inputfield import InputField
from ..schema import ObjectType, Schema
from ..mutation import Mutation


def test_enum_construction():
    class RGB(Enum):
        """Description"""

        RED = 1
        GREEN = 2
        BLUE = 3

        @property
        def description(self):
            return f"Description {self.name}"

    assert RGB._meta.name == "RGB"
    assert RGB._meta.description == "Description"

    values = RGB._meta.enum.__members__.values()
    assert sorted([v.name for v in values]) == ["BLUE", "GREEN", "RED"]
    assert sorted([v.description for v in values]) == [
        "Description BLUE",
        "Description GREEN",
        "Description RED",
    ]


def test_enum_construction_meta():
    class RGB(Enum):
        class Meta:
            name = "RGBEnum"
            description = "Description"

        RED = 1
        GREEN = 2
        BLUE = 3

    assert RGB._meta.name == "RGBEnum"
    assert RGB._meta.description == "Description"


def test_enum_instance_construction():
    RGB = Enum("RGB", "RED,GREEN,BLUE")

    values = RGB._meta.enum.__members__.values()
    assert sorted([v.name for v in values]) == ["BLUE", "GREEN", "RED"]


def test_enum_from_builtin_enum():
    PyRGB = PyEnum("RGB", "RED,GREEN,BLUE")

    RGB = Enum.from_enum(PyRGB)
    assert RGB._meta.enum == PyRGB
    assert RGB.RED
    assert RGB.GREEN
    assert RGB.BLUE


def test_enum_from_builtin_enum_accepts_lambda_description():
    def custom_description(value):
        if not value:
            return "StarWars Episodes"

        return "New Hope Episode" if value == Episode.NEWHOPE else "Other"

    def custom_deprecation_reason(value):
        return "meh" if value == Episode.NEWHOPE else None

    PyEpisode = PyEnum("PyEpisode", "NEWHOPE,EMPIRE,JEDI")
    Episode = Enum.from_enum(
        PyEpisode,
        description=custom_description,
        deprecation_reason=custom_deprecation_reason,
    )

    class Query(ObjectType):
        foo = Episode()

    schema = Schema(query=Query).graphql_schema

    episode = schema.get_type("PyEpisode")

    assert episode.description == "StarWars Episodes"
    assert [
        (name, value.description, value.deprecation_reason)
        for name, value in episode.values.items()
    ] == [
        ("NEWHOPE", "New Hope Episode", "meh"),
        ("EMPIRE", "Other", None),
        ("JEDI", "Other", None),
    ]


def test_enum_from_python3_enum_uses_enum_doc():
    from enum import Enum as PyEnum

    class Color(PyEnum):
        """This is the description"""

        RED = 1
        GREEN = 2
        BLUE = 3

    RGB = Enum.from_enum(Color)
    assert RGB._meta.enum == Color
    assert RGB._meta.description == "This is the description"
    assert RGB
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


def test_enum_can_be_initialized():
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

    assert RGB["RED"] == RGB.RED
    assert RGB["GREEN"] == RGB.GREEN
    assert RGB["BLUE"] == RGB.BLUE


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


def test_enum_skip_meta_from_members():
    class RGB1(Enum):
        class Meta:
            name = "RGB"

        RED = 1
        GREEN = 2
        BLUE = 3

    assert dict(RGB1._meta.enum.__members__) == {
        "RED": RGB1.RED,
        "GREEN": RGB1.GREEN,
        "BLUE": RGB1.BLUE,
    }


def test_enum_types():
    from enum import Enum as PyEnum

    class Color(PyEnum):
        """Primary colors"""

        RED = 1
        YELLOW = 2
        BLUE = 3

    GColor = Enum.from_enum(Color)

    class Query(ObjectType):
        color = GColor(required=True)

        def resolve_color(_, info):
            return Color.RED

    schema = Schema(query=Query)

    assert str(schema) == dedent(
        '''\
        type Query {
          color: Color!
        }

        """Primary colors"""
        enum Color {
          RED
          YELLOW
          BLUE
        }
    '''
    )


def test_enum_resolver():
    from enum import Enum as PyEnum

    class Color(PyEnum):
        RED = 1
        GREEN = 2
        BLUE = 3

    GColor = Enum.from_enum(Color)

    class Query(ObjectType):
        color = GColor(required=True)

        def resolve_color(_, info):
            return Color.RED

    schema = Schema(query=Query)

    results = schema.execute("query { color }")
    assert not results.errors

    assert results.data["color"] == Color.RED.name


def test_enum_resolver_compat():
    from enum import Enum as PyEnum

    class Color(PyEnum):
        RED = 1
        GREEN = 2
        BLUE = 3

    GColor = Enum.from_enum(Color)

    class Query(ObjectType):
        color = GColor(required=True)
        color_by_name = GColor(required=True)

        def resolve_color(_, info):
            return Color.RED.value

        def resolve_color_by_name(_, info):
            return Color.RED.name

    schema = Schema(query=Query)

    results = schema.execute(
        """query {
            color
            colorByName
        }"""
    )
    assert not results.errors

    assert results.data["color"] == Color.RED.name
    assert results.data["colorByName"] == Color.RED.name


def test_enum_resolver_invalid():
    from enum import Enum as PyEnum

    class Color(PyEnum):
        RED = 1
        GREEN = 2
        BLUE = 3

    GColor = Enum.from_enum(Color)

    class Query(ObjectType):
        color = GColor(required=True)

        def resolve_color(_, info):
            return "BLACK"

    schema = Schema(query=Query)

    results = schema.execute("query { color }")
    assert results.errors
    assert (
        results.errors[0].message
        == "Expected a value of type 'Color' but received: 'BLACK'"
    )


def test_enum_mutation():
    from enum import Enum as PyEnum

    class Color(PyEnum):
        RED = 1
        GREEN = 2
        BLUE = 3

    GColor = Enum.from_enum(Color)

    my_fav_color = None

    class Query(ObjectType):
        fav_color = GColor(required=True)

        def resolve_fav_color(_, info):
            return my_fav_color

    class SetFavColor(Mutation):
        class Arguments:
            fav_color = Argument(GColor, required=True)

        Output = Query

        def mutate(self, info, fav_color):
            nonlocal my_fav_color
            my_fav_color = fav_color
            return Query()

    class MyMutations(ObjectType):
        set_fav_color = SetFavColor.Field()

    schema = Schema(query=Query, mutation=MyMutations)

    results = schema.execute(
        """mutation {
            setFavColor(favColor: RED) {
                favColor
            }
        }"""
    )
    assert not results.errors

    assert my_fav_color == Color.RED

    assert results.data["setFavColor"]["favColor"] == Color.RED.name


def test_enum_mutation_compat():
    from enum import Enum as PyEnum

    class Color(PyEnum):
        RED = 1
        GREEN = 2
        BLUE = 3

    GColor = Enum.from_enum(Color)

    my_fav_color = None

    class Query(ObjectType):
        fav_color = GColor(required=True)

        def resolve_fav_color(_, info):
            return my_fav_color

    class SetFavColor(Mutation):
        class Arguments:
            fav_color = Argument(GColor, required=True)

        Output = Query

        def mutate(self, info, fav_color):
            nonlocal my_fav_color
            my_fav_color = fav_color
            return Query()

    class MyMutations(ObjectType):
        set_fav_color = SetFavColor.Field()

    schema = Schema(query=Query, mutation=MyMutations)

    results = schema.execute(
        """mutation {
            setFavColor(favColor: RED) {
                favColor
            }
        }""",
        middleware=[enum_value_convertor_middleware],
    )
    assert not results.errors

    assert my_fav_color == Color.RED.value

    assert results.data["setFavColor"]["favColor"] == Color.RED.name
