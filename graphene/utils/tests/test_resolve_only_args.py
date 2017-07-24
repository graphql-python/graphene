from ..resolve_only_args import resolve_only_args
from .. import deprecated


def test_resolve_only_args(mocker):
    mocker.patch.object(deprecated, 'warn_deprecation')
    def resolver(*args, **kwargs):
        return kwargs

    my_data = {'one': 1, 'two': 2}

    wrapped = resolve_only_args(resolver)
    assert deprecated.warn_deprecation.called
