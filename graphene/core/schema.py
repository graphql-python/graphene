from functools import wraps
from collections import OrderedDict

from graphql.core.type import (
    GraphQLSchema as _GraphQLSchema
)

from graphql.core.execution.executor import Executor
from graphql.core.execution.middlewares.sync import SynchronousExecutionMiddleware

from graphql.core.utils.introspection_query import introspection_query
from graphene import signals
from graphene.utils import cached_property


class GraphQLSchema(_GraphQLSchema):
    def __init__(self, schema, *args, **kwargs):
        self.graphene_schema = schema
        super(GraphQLSchema, self).__init__(*args, **kwargs)


class Schema(object):
    _query = None
    _executor = None

    def __init__(self, query=None, mutation=None, name='Schema', executor=None):
        self._internal_types = {}
        self._types = {}
        self.mutation = mutation
        self.query = query
        self.name = name
        self.executor = executor
        signals.init_schema.send(self)

    def __repr__(self):
        return '<Schema: %s (%s)>' % (str(self.name), hash(self))

    def T(self, object_type):
        if not object_type:
            return
        if object_type not in self._types:
            self._types[object_type] = object_type.internal_type(self)
        return self._types[object_type]

    @property
    def query(self):
        return self._query

    @query.setter
    def query(self, query):
        self._query = query

    @property
    def mutation(self):
        return self._mutation

    @mutation.setter
    def mutation(self, mutation):
        self._mutation = mutation

    @property
    def executor(self):
        if not self._executor:
            self.executor = Executor([SynchronousExecutionMiddleware()], map_type=OrderedDict)
        return self._executor

    @executor.setter
    def executor(self, value):
        self._executor = value

    @property
    def schema(self):
        if not self._query:
            raise Exception('You have to define a base query type')
        return GraphQLSchema(self, query=self.T(self._query), mutation=self.T(self._mutation))

    def associate_internal_type(self, internal_type, object_type):
        self._internal_types[internal_type.name] = object_type

    def register(self, object_type):
        self._internal_types[object_type._meta.type_name] = object_type
        return object_type

    def get_type(self, type_name):
        self.schema._build_type_map()
        if type_name not in self._internal_types:
            raise Exception('Type %s not found in %r' % (type_name, self))
        return self._internal_types[type_name]

    @property
    def types(self):
        return self._internal_types

    def execute(self, request='', root=None, vars=None, operation_name=None, **kwargs):
        root = root or object()
        return self.executor.execute(
            self.schema,
            request,
            root=self.query(root),
            args=vars,
            operation_name=operation_name,
            **kwargs
        )

    def introspect(self):
        return self.execute(introspection_query).data


def register_internal_type(fun):
    @wraps(fun)
    def wrapper(cls, schema):
        internal_type = fun(cls, schema)
        if isinstance(schema, Schema):
            schema.associate_internal_type(internal_type, cls)
        return internal_type

    return wrapper
