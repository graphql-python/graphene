from graphene.utils import ProxySnakeDict


def test_proxy_snake_dict():
    my_data = {'one': 1, 'two': 2, 'none': None, 'threeOrFor': 3, 'inside': {'otherCamelCase': 3}}
    p = ProxySnakeDict(my_data)
    assert 'one' in p
    assert 'two' in p
    assert 'threeOrFor' in p
    assert 'none' in p
    assert p['none'] is None
    assert p.get('none') is None
    assert p.get('none_existent') is None
    assert 'three_or_for' in p
    assert p.get('three_or_for') == 3
    assert 'inside' in p
    assert 'other_camel_case' in p['inside']


def test_proxy_snake_dict_as_kwargs():
    my_data = {'myData': 1}
    p = ProxySnakeDict(my_data)

    def func(**kwargs):
        return kwargs.get('my_data')
    assert func(**p) == 1
