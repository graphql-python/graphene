from functools import wraps


def with_context(func):
    setattr(func, 'with_context', 'context')
    return func


def wrap_resolver_function(func):
    @wraps(func)
    def inner(self, args, context, info):
        with_context = getattr(func, 'with_context', None)
        if with_context:
            return func(self, args, context, info)
        # For old compatibility
        return func(self, args, info)
    return inner
