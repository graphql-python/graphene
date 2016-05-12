from functools import wraps


def with_context(func):
    setattr(func, 'with_context', 'context')
    return func


def has_context(func):
    return getattr(func, 'with_context', None)


def wrap_resolver_function(func):
    @wraps(func)
    def inner(self, args, context, info):
        if has_context(func):
            return func(self, args, context, info)
        # For old compatibility
        return func(self, args, info)
    return inner
