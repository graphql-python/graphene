from functools import wraps


def resolve_only_args(func):
    @wraps(func)
    def inner(self, args, info):
        return func(self, **args)
    return inner
