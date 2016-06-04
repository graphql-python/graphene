from graphql import graphql, GraphQLSchema
from graphql.utils.introspection_query import introspection_query
from graphql.utils.schema_printer import print_schema

from ..utils.get_graphql_type import get_graphql_type


class Schema(GraphQLSchema):
    __slots__ = '_query', '_mutation', '_subscription', '_type_map', '_directives', '_implementations', '_possible_type_map', '_types', '_executor'

    def __init__(self, query=None, mutation=None, subscription=None, directives=None, types=None, executor=None):
        if query:
            query = get_graphql_type(query)
        if mutation:
            mutation = get_graphql_type(mutation)
        if subscription:
            subscription = get_graphql_type(subscription)
        if types:
            types = map(get_graphql_type, types)
        self._executor = executor
        super(Schema, self).__init__(
            query=query,
            mutation=mutation,
            subscription=subscription,
            directives=directives,
            types=types
        )

    def execute(self, request_string='', root_value=None, variable_values=None,
                context_value=None, operation_name=None, executor=None):
        return graphql(
            schema=self,
            request_string=request_string,
            root_value=root_value,
            context_value=context_value,
            variable_values=variable_values,
            operation_name=operation_name,
            executor=executor or self._executor
        )

    def register(self, object_type):
        self._types.append(object_type)

    def introspect(self):
        return self.execute(introspection_query).data

    def __str__(self):
        return print_schema(self)

    def get_type(self, _type):
        return self._type_map[_type]

    def lazy(self, _type):
        return lambda: self.get_type(_type)
