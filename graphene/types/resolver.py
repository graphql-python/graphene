def attr_resolver(attname, default_value, root, args, context, info):
    return getattr(root, attname, default_value)


def dict_resolver(attname, default_value, root, args, context, info):
    return root.get(attname, default_value)


default_resolver = attr_resolver


def set_default_resolver(resolver):
    global default_resolver
    assert callable(resolver), 'Received non-callable resolver.'
    default_resolver = resolver


def get_default_resolver():
    return default_resolver
