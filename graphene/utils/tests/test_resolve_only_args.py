from ..resolve_only_args import resolve_only_args


def test_resolve_only_args():
    my_data = {'one': 1, 'two': 2}
    resolver = lambda *args, **kwargs: kwargs
    wrapped = resolve_only_args(resolver)
    assert wrapped(None, my_data, None) == my_data
