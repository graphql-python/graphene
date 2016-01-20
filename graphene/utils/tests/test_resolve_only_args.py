from ..resolve_only_args import resolve_only_args


def test_resolve_only_args():

    def resolver(*args, **kwargs):
        return kwargs

    my_data = {'one': 1, 'two': 2}

    wrapped = resolve_only_args(resolver)
    assert wrapped(None, my_data, None) == my_data
