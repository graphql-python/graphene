from .enum import PyEnum


def attr_resolver(attname, default_value, root, info, **args):
    value = getattr(root, attname, default_value)
    if isinstance(value, PyEnum):
        return value.value
    return value


def dict_resolver(attname, default_value, root, info, **args):
    return root.get(attname, default_value)


default_resolver = attr_resolver


def set_default_resolver(resolver):
    global default_resolver
    assert callable(resolver), 'Received non-callable resolver.'
    default_resolver = resolver


def get_default_resolver():
    return default_resolver
