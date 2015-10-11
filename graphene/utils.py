from functools import wraps


class cached_property(object):
    """
    A property that is only computed once per instance and then replaces itself
    with an ordinary attribute. Deleting the attribute resets the property.
    Source: https://github.com/bottlepy/bottle/commit/fa7733e075da0d790d809aa3d2f53071897e6f76
    """  # noqa

    def __init__(self, func):
        self.__doc__ = getattr(func, '__doc__')
        self.func = func

    def __get__(self, obj, cls):
        if obj is None:
            return self
        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value


def memoize(fun):
    """A simple memoize decorator for functions supporting positional args."""
    @wraps(fun)
    def wrapper(*args, **kwargs):
        key = (args, frozenset(sorted(kwargs.items())))
        try:
            return cache[key]
        except KeyError:
            ret = cache[key] = fun(*args, **kwargs)
        return ret
    cache = {}
    return wrapper


# From this response in Stackoverflow
# http://stackoverflow.com/a/19053800/1072990
def to_camel_case(snake_str):
    components = snake_str.split('_')
    # We capitalize the first letter of each component except the first one
    # with the 'title' method and join them together.
    return components[0] + "".join(x.title() for x in components[1:])


class LazyMap(object):
    def __init__(self, origin, _map, state=None):
        self._origin = origin
        self._origin_iter = origin.__iter__()
        self._state = state or []
        self._finished = False
        self._map = _map

    def __iter__(self):
        return self if not self._finished else iter(self._state)

    def iter(self):
        return self.__iter__()

    def __len__(self):
        return self._origin.__len__()

    def __next__(self):
        try:
            n = next(self._origin_iter)
            n = self._map(n)
        except StopIteration as e:
            self._finished = True
            raise e
        else:
            self._state.append(n)
            return n

    def next(self):
        return self.__next__()

    def __getitem__(self, key):
        item = self._origin.__getitem__(key)
        if isinstance(key, slice):
            return LazyMap(item, self._map)
        return self._map(item)

    def __getattr__(self, name):
        return getattr(self._origin, name)

    def __repr__(self):
        return "<LazyMap %s>" % repr(self._origin)
