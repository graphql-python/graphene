from ..orderedtype import OrderedType


def test_orderedtype():
    one = OrderedType()
    two = OrderedType()
    three = OrderedType()

    assert one < two < three


def test_orderedtype_eq():
    one = OrderedType()
    two = OrderedType()

    assert one == one
    assert one != two


def test_orderedtype_hash():
    one = OrderedType()
    two = OrderedType()

    assert hash(one) == hash(one)
    assert hash(one) != hash(two)
