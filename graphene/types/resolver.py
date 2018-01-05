def attr_resolver(attname, default_value, root, info, **args):
    return getattr(root, attname, default_value)


def dict_resolver(attname, default_value, root, info, **args):
    return root.get(attname, default_value)


def dict_or_attr_resolver(attname, default_value, root, info, **args):
    if isinstance(root, dict):
        return dict_resolver(attname, default_value, root, info, **args)
    return attr_resolver(attname, default_value, root, info, **args)


default_resolver = dict_or_attr_resolver


def set_default_resolver(resolver):
    global default_resolver
    assert callable(resolver), "Received non-callable resolver."
    default_resolver = resolver


def get_default_resolver():
    return default_resolver
