from ..maybe_func import maybe_func


def maybe_func_function():
    assert maybe_func(lambda: True) is True


def maybe_func_value():
    assert maybe_func(True) is True
