from graphql.core import graphql
from graphql.core.type import (
    GraphQLSchema
)
from graphene import signals
from graphene.utils import cached_property
# from graphene.relay.nodes import create_node_definitions

class Schema(object):
    _query = None

    def __init__(self, query=None, mutation=None, name='Schema'):
        self.mutation = mutation
        self.query = query
        self.name = name
        self._types = {}
        
    def __repr__(self):
        return '<Schema: %s>' % str(self.name)

    # @cachedproperty
    # def node_definitions(self):
    #     return [object, object]
    #     # from graphene.relay import create_node_definitions
    #     # return create_node_definitions(schema=self)

    # @property
    # def Node(self):
    #     return self.node_definitions[0]

    # @property
    # def NodeField(self):
    #     return self.node_definitions[1]

    @property
    def query(self):
        return self._query
    @query.setter
    def query(self, query):
        if not query:
            return
        self._query = query
        self._query_type = query._meta.type
        self._schema = GraphQLSchema(query=self._query_type, mutation=self.mutation)

    def register_type(self, type):
        type_name = type._meta.type_name
        if type_name in self._types:
            raise Exception('Type name %s already registered in %r' % (type_name, self))
        self._types[type_name] = type

    def get_type(self, type_name):
        if type_name not in self._types:
            raise Exception('Type %s not found in %r' % (type_name, self))
        return self._types[type_name]

    def execute(self, request='', root=None, vars=None, operation_name=None):
        return graphql(
            self._schema,
            request=request,
            root=root or self.query(),
            vars=vars,
            operation_name=operation_name
        )


@signals.class_prepared.connect
def object_type_created(object_type):
    schema = object_type._meta.schema
    if schema:
        schema.register_type(object_type)

from graphene.env import get_global_schema
