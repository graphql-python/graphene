from py.test import raises

from ..proxy_snake_dict import ProxySnakeDict


def test_proxy_snake_dict():
    my_data = {'one': 1, 'two': 2, 'none': None,
               'threeOrFor': 3, 'inside': {'otherCamelCase': 3}}
    p = ProxySnakeDict(my_data)
    assert 'one' in p
    assert 'two' in p
    assert 'threeOrFor' in p
    assert 'none' in p
    assert len(p) == len(my_data)
    assert p['none'] is None
    assert p.get('none') is None
    assert p.get('none_existent') is None
    assert 'three_or_for' in p
    assert p.get('three_or_for') == 3
    assert 'inside' in p
    assert 'other_camel_case' in p['inside']
    assert sorted(
        p.items()) == sorted(
        list(
            [('inside', ProxySnakeDict({'other_camel_case': 3})),
             ('none', None),
             ('three_or_for', 3),
             ('two', 2),
             ('one', 1)]))


def test_proxy_snake_dict_as_kwargs():
    my_data = {'myData': 1}
    p = ProxySnakeDict(my_data)

    def func(**kwargs):
        return kwargs.get('my_data')
    assert func(**p) == 1


def test_proxy_snake_dict_repr():
    my_data = {'myData': 1}
    p = ProxySnakeDict(my_data)

    assert repr(p) == "<ProxySnakeDict {'my_data': 1}>"


def test_proxy_snake_dict_set():
    p = ProxySnakeDict({})
    with raises(TypeError):
        p['a'] = 2


def test_proxy_snake_dict_delete():
    p = ProxySnakeDict({})
    with raises(TypeError):
        del p['a']
