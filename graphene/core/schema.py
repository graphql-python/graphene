import inspect
from collections import OrderedDict

from graphql.core.execution.executor import Executor
from graphql.core.execution.middlewares.sync import \
    SynchronousExecutionMiddleware
from graphql.core.type import GraphQLSchema as _GraphQLSchema
from graphql.core.utils.introspection_query import introspection_query
from graphql.core.utils.schema_printer import print_schema

from graphene import signals

from ..plugins import CamelCase, PluginManager
from .classtypes.base import ClassType
from .types.base import InstanceType


class GraphQLSchema(_GraphQLSchema):

    def __init__(self, schema, *args, **kwargs):
        self.graphene_schema = schema
        super(GraphQLSchema, self).__init__(*args, **kwargs)


class Schema(object):
    _executor = None

    def __init__(self, query=None, mutation=None, subscription=None,
                 name='Schema', executor=None, plugins=None, auto_camelcase=True):
        self._types_names = {}
        self._types = {}
        self.mutation = mutation
        self.query = query
        self.subscription = subscription
        self.name = name
        self.executor = executor
        plugins = plugins or []
        if auto_camelcase:
            plugins.append(CamelCase())
        self.plugins = PluginManager(self, plugins)
        signals.init_schema.send(self)

    def __repr__(self):
        return '<Schema: %s (%s)>' % (str(self.name), hash(self))

    def __getattr__(self, name):
        if name in self.plugins:
            return getattr(self.plugins, name)
        return super(Schema, self).__getattr__(name)

    def T(self, _type):
        if not _type:
            return
        is_classtype = inspect.isclass(_type) and issubclass(_type, ClassType)
        is_instancetype = isinstance(_type, InstanceType)
        if is_classtype or is_instancetype:
            if _type not in self._types:
                internal_type = _type.internal_type(self)
                self._types[_type] = internal_type
                if is_classtype:
                    self.register(_type)
            return self._types[_type]
        else:
            return _type

    @property
    def executor(self):
        if not self._executor:
            self._executor = Executor(
                [SynchronousExecutionMiddleware()], map_type=OrderedDict)
        return self._executor

    @executor.setter
    def executor(self, value):
        self._executor = value

    @property
    def schema(self):
        if not self.query:
            raise Exception('You have to define a base query type')
        return GraphQLSchema(
            self,
            query=self.T(self.query),
            mutation=self.T(self.mutation),
            subscription=self.T(self.subscription))

    def register(self, object_type, force=False):
        type_name = object_type._meta.type_name
        registered_object_type = not force and self._types_names.get(type_name, None)
        if registered_object_type:
            assert registered_object_type == object_type, 'Type {} already registered with other object type'.format(
                type_name)
        self._types_names[object_type._meta.type_name] = object_type
        return object_type

    def objecttype(self, type):
        name = getattr(type, 'name', None)
        if name:
            objecttype = self._types_names.get(name, None)
            if objecttype and inspect.isclass(
                    objecttype) and issubclass(objecttype, ClassType):
                return objecttype

    def __str__(self):
        return print_schema(self.schema)

    def setup(self):
        assert self.query, 'The base query type is not set'
        self.T(self.query)

    def get_type(self, type_name):
        self.setup()
        if type_name not in self._types_names:
            raise KeyError('Type %r not found in %r' % (type_name, self))
        return self._types_names[type_name]

    @property
    def types(self):
        return self._types_names

    def execute(self, request='', root=None, args=None, **kwargs):
        kwargs = dict(kwargs, request=request, root=root, args=args, schema=self.schema)
        with self.plugins.context_execution(**kwargs) as execute_kwargs:
            return self.executor.execute(**execute_kwargs)

    def introspect(self):
        return self.execute(introspection_query).data
