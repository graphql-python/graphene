from ..utils.comparison_helper import raise_assertion_if_true

def attr_resolver(attname, default_value, root, info, **args):
    return getattr(root, attname, default_value)


def dict_resolver(attname, default_value, root, info, **args):
    return root.get(attname, default_value)


default_resolver = attr_resolver


def set_default_resolver(resolver):
    global default_resolver

    raise_assertion_if_true(
        condition=not callable(resolver),
        message="Received non-callable resolver."
    )
    default_resolver = resolver


def get_default_resolver():
    return default_resolver
