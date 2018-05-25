from ..dynamic import Dynamic
from ..scalars import String
from ..structures import List
from ..structures import NonNull


def test_dynamic():
    dynamic = Dynamic(lambda: String)
    assert dynamic.get_type() == String
    assert str(dynamic.get_type()) == 'String'


def test_nonnull():
    dynamic = Dynamic(lambda: NonNull(String))
    assert dynamic.get_type().of_type == String
    assert str(dynamic.get_type()) == 'String!'


def test_list():
    dynamic = Dynamic(lambda: List(String))
    assert dynamic.get_type().of_type == String
    assert str(dynamic.get_type()) == '[String]'


def test_list_non_null():
    dynamic = Dynamic(lambda: List(NonNull(String)))
    assert dynamic.get_type().of_type.of_type == String
    assert str(dynamic.get_type()) == '[String!]'
