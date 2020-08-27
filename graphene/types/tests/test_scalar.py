from ..scalars import Scalar, Int, BigInt


def test_scalar():
    class JSONScalar(Scalar):
        """Documentation"""

    assert JSONScalar._meta.name == "JSONScalar"
    assert JSONScalar._meta.description == "Documentation"


def test_ints():
    assert Int.parse_value(2 ** 31 - 1) is not None
    assert Int.parse_value(2 ** 31) is None

    assert Int.parse_value(-2 ** 31) is not None
    assert Int.parse_value(-2 ** 31 - 1) is None

    assert BigInt.parse_value(2 ** 31) is not None
    assert BigInt.parse_value(-2 ** 31 - 1) is not None
