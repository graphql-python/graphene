class _OldClass:
    pass


class _NewClass(object):
    pass


_all_vars = set(dir(_OldClass) + dir(_NewClass))


def props(x):
    return {
        key: value for key, value in vars(x).items() if key not in _all_vars
    }
