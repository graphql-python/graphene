from .resolver_from_annotations import resolver_from_annotations


def final_resolver(func):
    func._is_final_resolver = True
    return func


def auto_resolver(func=None):
    if not func:
        return

    if not is_final_resolver(func):
        # Is a Graphene 2.0 resolver function
        return final_resolver(resolver_from_annotations(func))
    else:
        return func


def is_final_resolver(func):
    return getattr(func, '_is_final_resolver', False)
