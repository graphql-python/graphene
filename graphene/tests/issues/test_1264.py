from graphene.types.enum import Enum


def test_enum_iteration():
    class TestEnum(Enum):
        FIRST = 1
        SECOND = 2

    result = []
    expected_values = ["FIRST", "SECOND"]
    for c in TestEnum:
        result.append(c.name)
    assert result == expected_values
