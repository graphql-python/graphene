from __future__ import absolute_import

from graphql.pyutils.compat import Enum

try:
    from inspect import signature
except ImportError:
    from .signature import signature
