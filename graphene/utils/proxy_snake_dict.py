import collections

from .str_converters import to_camel_case, to_snake_case


class ProxySnakeDict(collections.MutableMapping):
    __slots__ = ('data')

    def __init__(self, data):
        self.data = data

    def __contains__(self, key):
        return key in self.data or to_camel_case(key) in self.data

    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def __iter__(self):
        return self.iterkeys()

    def __len__(self):
        return len(self.data)

    def __delitem__(self, item):
        raise TypeError('ProxySnakeDict does not support item deletion')

    def __setitem__(self, item, value):
        raise TypeError('ProxySnakeDict does not support item assignment')

    def __getitem__(self, key):
        if key in self.data:
            item = self.data[key]
        else:
            camel_key = to_camel_case(key)
            if camel_key in self.data:
                item = self.data[camel_key]
            else:
                raise KeyError(key, camel_key)

        if isinstance(item, dict):
            return ProxySnakeDict(item)
        return item

    def keys(self):
        return list(self.iterkeys())

    def items(self):
        return list(self.iteritems())

    def iterkeys(self):
        for k in self.data.keys():
            yield to_snake_case(k)
        return

    def iteritems(self):
        for k in self.iterkeys():
            yield k, self[k]

    def to_data_dict(self):
        return self.data.__class__(self.iteritems())

    def __eq__(self, other):
        return self.to_data_dict() == other.to_data_dict()

    def __repr__(self):
        data_repr = self.to_data_dict().__repr__()
        return '<ProxySnakeDict {}>'.format(data_repr)
