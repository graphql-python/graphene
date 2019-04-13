from enum import Enum as PyEnum

from ..objecttype import ObjectType
from ..scalars import String
from ..schema import Schema

from ..enum import Enum


class PythonEnum(PyEnum):
    P1 = "p1"
    P2 = "p2"


PythonBaseEnum = Enum.from_enum(PythonEnum, legacy_enum_resolver=False)


class Query(ObjectType):
    python = String(v=PythonBaseEnum(default_value=PythonBaseEnum.P1))

    def resolve_python(self, _, v):
        return "python"


def test_fixture_sane():
    """Check that the fixture enums are built correctly"""
    assert PythonBaseEnum.P1.value == "p1"
    assert PythonBaseEnum.P2.value == "p2"

    assert PythonBaseEnum.P1 != "p1"
    assert PythonBaseEnum.P2 != "p2"


def _call_and_get_arg(mocker, resolver_name, query):
    resolver = mocker.patch.object(Query, resolver_name, return_value="mocked")
    schema = Schema(Query)

    r = schema.execute(query)
    assert not r.errors

    assert resolver.call_count == 1

    return resolver.call_args[1]["v"]


def test_resolve_enum_python(mocker):
    arg = _call_and_get_arg(mocker, "resolve_python", "{python(v:P2)}")
    assert arg is PythonBaseEnum.P2
    assert arg is not PythonBaseEnum.P2.value
    assert arg is PythonEnum.P2
    assert arg is not PythonEnum.P2.value


def test_resolve_enum_default_value_python(mocker):
    param = _call_and_get_arg(mocker, "resolve_python", "{python}")
    assert param == PythonBaseEnum.P1
