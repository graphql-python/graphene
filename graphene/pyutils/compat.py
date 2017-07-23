from __future__ import absolute_import

try:
    from enum import Enum
except ImportError:
    from .enum import Enum

try:
    from inspect import signature
except ImportError:
    from .signature import signature
