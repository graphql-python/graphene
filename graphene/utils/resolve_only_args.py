from functools import wraps


def resolve_only_args(func):
    @wraps(func)
    def inner(root, args, context, info):
        return func(root, **args)
    return inner
