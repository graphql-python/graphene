import inspect
from collections import OrderedDict

from graphene import signals
from graphene.core.types.base import BaseType
from graphene.core.types.objecttype import BaseObjectType
from graphql.core.execution.executor import Executor
from graphql.core.execution.middlewares.sync import \
    SynchronousExecutionMiddleware
from graphql.core.type import GraphQLSchema as _GraphQLSchema
from graphql.core.utils.introspection_query import introspection_query


class GraphQLSchema(_GraphQLSchema):

    def __init__(self, schema, *args, **kwargs):
        self.graphene_schema = schema
        super(GraphQLSchema, self).__init__(*args, **kwargs)


class Schema(object):
    _executor = None

    def __init__(self, query=None, mutation=None, name='Schema', executor=None):
        self._types_names = {}
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
        if inspect.isclass(object_type) and issubclass(object_type, BaseType) or isinstance(object_type, BaseType):
            if object_type not in self._types:
                internal_type = object_type.internal_type(self)
                self._types[object_type] = internal_type
                is_objecttype = inspect.isclass(
                    object_type) and issubclass(object_type, BaseObjectType)
                if is_objecttype:
                    self.register(object_type)
            return self._types[object_type]
        else:
            return object_type

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
        return GraphQLSchema(self, query=self.T(self.query), mutation=self.T(self.mutation))

    def register(self, object_type):
        type_name = object_type._meta.type_name
        registered_object_type = self._types_names.get(type_name, None)
        if registered_object_type:
            assert registered_object_type == object_type, 'Type {} already registered with other object type'.format(
                type_name)
        self._types_names[object_type._meta.type_name] = object_type
        return object_type

    def objecttype(self, type):
        name = getattr(type, 'name', None)
        if name:
            objecttype = self._types_names.get(name, None)
            if objecttype and inspect.isclass(objecttype) and issubclass(objecttype, BaseObjectType):
                return objecttype

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
