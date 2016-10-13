import pytest

from ..structures import List, NonNull
from ..scalars import String


def test_list():
    _list = List(String)
    assert _list.of_type == String
    assert str(_list) == '[String]'


def test_nonnull():
    nonnull = NonNull(String)
    assert nonnull.of_type == String
    assert str(nonnull) == 'String!'


def test_list_comparasion():
    list1 = List(String)
    list2 = List(String)
    list3 = List(None)

    list1_argskwargs = List(String, None, b=True)
    list2_argskwargs = List(String, None, b=True)

    assert list1 == list2
    assert list1 != list3
    assert list1_argskwargs == list2_argskwargs
    assert list1 != list1_argskwargs


def test_nonnull_comparasion():
    nonnull1 = NonNull(String)
    nonnull2 = NonNull(String)
    nonnull3 = NonNull(None)

    nonnull1_argskwargs = NonNull(String, None, b=True)
    nonnull2_argskwargs = NonNull(String, None, b=True)

    assert nonnull1 == nonnull2
    assert nonnull1 != nonnull3
    assert nonnull1_argskwargs == nonnull2_argskwargs
    assert nonnull1 != nonnull1_argskwargs
