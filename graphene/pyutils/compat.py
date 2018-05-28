from __future__ import absolute_import

import six

try:
    from enum import Enum
except ImportError:
    from .enum import Enum

try:
    from inspect import signature
except ImportError:
    from .signature import signature

if six.PY2:
    def func_name(func):
        return func.func_name
else:
    def func_name(func):
        return func.__name__
