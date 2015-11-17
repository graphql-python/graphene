from py.test import raises

from ..lazymap import LazyMap


def test_lazymap():
    data = list(range(10))
    lm = LazyMap(data, lambda x: 2 * x)
    assert len(lm) == 10
    assert lm[1] == 2
    assert isinstance(lm[1:4], LazyMap)
    assert lm.append == data.append
    assert repr(lm) == '<LazyMap [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]>'


def test_lazymap_iter():
    data = list(range(2))
    lm = LazyMap(data, lambda x: 2 * x)
    iter_lm = iter(lm)
    assert iter_lm.next() == 0
    assert iter_lm.next() == 2
    with raises(StopIteration):
        iter_lm.next()
