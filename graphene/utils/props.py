class _Class:
    pass


_built_in_vars = set(dir(_Class))


def props(x):
    return {
        key: vars(x).get(key, getattr(x, key)) for key in dir(x) if key not in _built_in_vars
    }
