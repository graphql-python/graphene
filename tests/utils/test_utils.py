from graphene.utils import ProxySnakeDict, to_snake_case


def test_snake_case():
    assert to_snake_case('snakesOnAPlane') == 'snakes_on_a_plane'
    assert to_snake_case('SnakesOnAPlane') == 'snakes_on_a_plane'
    assert to_snake_case('snakes_on_a_plane') == 'snakes_on_a_plane'
    assert to_snake_case('IPhoneHysteria') == 'i_phone_hysteria'
    assert to_snake_case('iPhoneHysteria') == 'i_phone_hysteria'


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


