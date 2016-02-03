import inspect


def maybe_func(f):
    if inspect.isfunction(f):
        return f()
    return f
