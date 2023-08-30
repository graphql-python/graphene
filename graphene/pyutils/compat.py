from graphql.pyutils.compat import Enum

try:
    from inspect import signature
except ImportError:
    from .signature import signature


def func_name(func):
    return func.__name__
