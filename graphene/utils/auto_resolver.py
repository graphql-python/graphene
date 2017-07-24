from .resolver_from_annotations import resolver_from_annotations, is_wrapped_from_annotations


def auto_resolver(func=None):
    annotations = getattr(func, '__annotations__', {})
    is_annotated = getattr(func, '_is_annotated', False)

    if (annotations or is_annotated) and not is_wrapped_from_annotations(func):
        # Is a Graphene 2.0 resolver function
        return resolver_from_annotations(func)
    else:
        return func
