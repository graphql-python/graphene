from contextlib import contextmanager
from django.db import connections

from ....plugins import Plugin
from ....core.schema import Schema
from ....core.types import Field
from .sql.tracking import unwrap_cursor, wrap_cursor
from .sql.types import DjangoDebugSQL
from .types import DjangoDebug


class WrappedRoot(object):

    def __init__(self, root):
        self._recorded = []
        self._root = root

    def record(self, **log):
        self._recorded.append(DjangoDebugSQL(**log))

    def debug(self):
        return DjangoDebug(sql=self._recorded)


class WrapRoot(object):

    @property
    def _root(self):
        return self._wrapped_root.root

    @_root.setter
    def _root(self, value):
        self._wrapped_root = value

    def resolve_debug(self, args, info):
        return self._wrapped_root.debug()


def debug_objecttype(objecttype):
    return type(
        'Debug{}'.format(objecttype._meta.type_name),
        (WrapRoot, objecttype),
        {'debug': Field(DjangoDebug, name='__debug')})


class DjangoDebugPlugin(Plugin):
    def transform_type(self, _type):
        if _type == self.schema.query:
            return debug_objecttype(_type)
        return _type

    def enable_instrumentation(self, wrapped_root):
        # This is thread-safe because database connections are thread-local.
        for connection in connections.all():
            wrap_cursor(connection, wrapped_root)

    def disable_instrumentation(self):
        for connection in connections.all():
            unwrap_cursor(connection)

    @contextmanager
    def context_execution(self, executor):
        executor['root'] = WrappedRoot(root=executor['root'])
        self.enable_instrumentation(executor['root'])
        yield executor
        self.disable_instrumentation()
