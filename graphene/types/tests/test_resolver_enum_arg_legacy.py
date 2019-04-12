from enum import Enum as PyEnum

from ..objecttype import ObjectType
from ..scalars import String
from ..schema import Schema

from ..enum import Enum


class SimpleEnum(Enum):
    S1 = "s1"
    S2 = "s2"


class PythonEnum(PyEnum):
    P1 = "p1"
    P2 = "p2"


PythonBaseEnum = Enum.from_enum(PythonEnum)

FunctionalEnum = Enum("Functional", [("F1", "f1"), ("F2", "f2")])


class Query(ObjectType):
    simple = String(v=SimpleEnum(default_value=SimpleEnum.S1))
    python = String(v=PythonBaseEnum(default_value=PythonBaseEnum.P1))
    functional = String(v=FunctionalEnum(default_value=FunctionalEnum.F1))

    def resolve_simple(self, _, v):
        return "simple"

    def resolve_python(self, _, v):
        return "python"

    def resolve_functional(self, _, v):
        return "functional"


def test_fixture_sane():
    """Check that the fixture enums are built correctly"""
    assert SimpleEnum.S1.value == "s1"
    assert SimpleEnum.S2.value == "s2"

    assert PythonBaseEnum.P1.value == "p1"
    assert PythonBaseEnum.P2.value == "p2"

    assert FunctionalEnum.F1.value == "f1"
    assert FunctionalEnum.F2.value == "f2"


def _call(schema, query):
    r = schema.execute("{simple}")
    assert not r.errors
    return r.data


def _call_and_get_arg(mocker, resolver_name, query):
    resolver = mocker.patch.object(Query, resolver_name, return_value="mocked")
    schema = Schema(Query)

    r = schema.execute(query)
    assert not r.errors

    assert resolver.call_count == 1

    return resolver.call_args[1]["v"]


def test_resolve_simple_enum(mocker):
    arg = _call_and_get_arg(mocker, "resolve_simple", "{simple(v:S2)}")
    assert arg == SimpleEnum.S2.value


def test_resolve_enum_python(mocker):
    arg = _call_and_get_arg(mocker, "resolve_python", "{python(v:P2)}")
    assert arg == PythonBaseEnum.P2.value
    assert arg == PythonEnum.P2.value


def test_resolve_enum_functional_api(mocker):
    arg = _call_and_get_arg(mocker, "resolve_functional", "{functional(v:F2)}")
    assert arg == FunctionalEnum.F2.value


def test_resolve_enum_default_value_simple(mocker):
    param = _call_and_get_arg(mocker, "resolve_simple", "{simple}")
    assert param == SimpleEnum.S1


def test_resolve_enum_default_value_python(mocker):
    param = _call_and_get_arg(mocker, "resolve_python", "{python}")
    assert param == PythonBaseEnum.P1


def test_resolve_enum_default_value_functional(mocker):
    param = _call_and_get_arg(mocker, "resolve_functional", "{functional}")
    assert param == FunctionalEnum.F1
