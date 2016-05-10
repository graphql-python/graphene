from contextlib import contextmanager

from django.db import connections

from ....core.schema import GraphQLSchema
from ....core.types import Field
from ....plugins import Plugin
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

    def enable_instrumentation(self, wrapped_root):
        # This is thread-safe because database connections are thread-local.
        for connection in connections.all():
            wrap_cursor(connection, wrapped_root)

    def disable_instrumentation(self):
        for connection in connections.all():
            unwrap_cursor(connection)

    def wrap_schema(self, schema_type):
        query = schema_type._query
        if query:
            class_type = self.schema.objecttype(schema_type.get_query_type())
            assert class_type, 'The query in schema is not constructed with graphene'
            _type = debug_objecttype(class_type)
            self.schema.register(_type, force=True)
            return GraphQLSchema(
                self.schema,
                self.schema.T(_type),
                schema_type.get_mutation_type(),
                schema_type.get_subscription_type()
            )
        return schema_type

    @contextmanager
    def context_execution(self, executor):
        executor['root_value'] = WrappedRoot(root=executor.get('root_value'))
        executor['schema'] = self.wrap_schema(executor['schema'])
        self.enable_instrumentation(executor['root_value'])
        yield executor
        self.disable_instrumentation()
