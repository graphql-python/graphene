from __future__ import absolute_import

try:
    from inspect import signature
except ImportError:
    from .signature import signature
