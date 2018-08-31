"""
This file is used mainly as a bridge for thenable abstractions.
This includes:
- Promises
- Asyncio Coroutines
"""

try:
    from promise import Promise, is_thenable  # type: ignore
except ImportError:

    class Promise(object):  # type: ignore
        pass

    def is_thenable(obj):  # type: ignore
        return False


try:
    from inspect import isawaitable
    from .thenables_asyncio import await_and_execute
except ImportError:

    def isawaitable(obj):  # type: ignore
        return False


def maybe_thenable(obj, on_resolve):
    """
    Execute a on_resolve function once the thenable is resolved,
    returning the same type of object inputed.
    If the object is not thenable, it should return on_resolve(obj)
    """
    if isawaitable(obj) and not isinstance(obj, Promise):
        return await_and_execute(obj, on_resolve)

    if is_thenable(obj):
        return Promise.resolve(obj).then(on_resolve)

    # If it's not awaitable not a Promise, return
    # the function executed over the object
    return on_resolve(obj)
