from ..scalars import Scalar, Int, BigInt
from graphql.language.ast import IntValueNode


def test_scalar():
    class JSONScalar(Scalar):
        """Documentation"""

    assert JSONScalar._meta.name == "JSONScalar"
    assert JSONScalar._meta.description == "Documentation"


def test_ints():
    assert Int.parse_value(2**31 - 1) is not None
    assert Int.parse_value("2.0") is not None
    assert Int.parse_value(2**31) is None

    assert Int.parse_literal(IntValueNode(value=str(2**31 - 1))) == 2**31 - 1
    assert Int.parse_literal(IntValueNode(value=str(2**31))) is None

    assert Int.parse_value(-(2**31)) is not None
    assert Int.parse_value(-(2**31) - 1) is None

    assert BigInt.parse_value(2**31) is not None
    assert BigInt.parse_value("2.0") is not None
    assert BigInt.parse_value(-(2**31) - 1) is not None

    assert BigInt.parse_literal(IntValueNode(value=str(2**31 - 1))) == 2**31 - 1
    assert BigInt.parse_literal(IntValueNode(value=str(2**31))) == 2**31
