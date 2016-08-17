
from graphql import GraphQLSchema, MiddlewareManager, graphql, is_type
from graphql.type.directives import (GraphQLDirective, GraphQLIncludeDirective,
                                     GraphQLSkipDirective)
from graphql.type.introspection import IntrospectionSchema
from graphql.utils.introspection_query import introspection_query
from graphql.utils.schema_printer import print_schema

from .typemap import TypeMap, is_graphene_type


class Schema(GraphQLSchema):
    '''
    Schema Definition

    A Schema is created by supplying the root types of each type of operation,
    query and mutation (optional). A schema definition is then supplied to the
    validator and executor.
    '''

    def __init__(self, query=None, mutation=None, subscription=None,
                 directives=None, types=None, executor=None, middlewares=None):
        self._query = query
        self._mutation = mutation
        self._subscription = subscription
        self.types = types
        self._executor = executor
        if directives is None:
            directives = [
                GraphQLIncludeDirective,
                GraphQLSkipDirective
            ]

        assert all(isinstance(d, GraphQLDirective) for d in directives), \
            'Schema directives must be List[GraphQLDirective] if provided but got: {}.'.format(
                directives
        )
        if middlewares:
            self.middlewares = MiddlewareManager(*middlewares)
        else:
            self.middlewares = None
        self._directives = directives
        self.build_typemap()

    def get_query_type(self):
        return self.get_graphql_type(self._query)

    def get_mutation_type(self):
        return self.get_graphql_type(self._mutation)

    def get_subscription_type(self):
        return self.get_graphql_type(self._subscription)

    def get_graphql_type(self, _type):
        if not _type:
            return _type
        if is_type(_type):
            return _type
        if is_graphene_type(_type):
            graphql_type = self.get_type(_type._meta.name)
            assert graphql_type, "Type {} not found in this schema.".format(_type._meta.name)
            assert graphql_type.graphene_type == _type
            return graphql_type
        raise Exception("{} is not a valid GraphQL type.".format(_type))

    def execute(self, request_string='', root_value=None, variable_values=None,
                context_value=None, operation_name=None, executor=None):
        return graphql(
            schema=self,
            request_string=request_string,
            root_value=root_value,
            context_value=context_value,
            variable_values=variable_values,
            operation_name=operation_name,
            executor=executor or self._executor,
            middlewares=self.middlewares
        )

    def register(self, object_type):
        self.types.append(object_type)

    def introspect(self):
        return self.execute(introspection_query).data

    def __str__(self):
        return print_schema(self)

    def lazy(self, _type):
        return lambda: self.get_type(_type)

    def build_typemap(self):
        initial_types = [
            self._query,
            self._mutation,
            self._subscription,
            IntrospectionSchema
        ]
        if self.types:
            initial_types += self.types
        self._type_map = TypeMap(initial_types)
