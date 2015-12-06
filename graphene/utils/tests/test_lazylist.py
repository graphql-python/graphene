from py.test import raises

from ..lazylist import LazyList


def test_lazymap():
    data = list(range(10))
    lm = LazyList(data)
    assert len(lm) == 10
    assert lm[1] == 1
    assert isinstance(lm[1:4], LazyList)
    assert lm.append == data.append
    assert repr(lm) == '<LazyList [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]>'


def test_lazymap_iter():
    data = list(range(2))
    lm = LazyList(data)
    iter_lm = iter(lm)
    assert iter_lm.next() == 0
    assert iter_lm.next() == 1
    with raises(StopIteration):
        iter_lm.next()
