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
