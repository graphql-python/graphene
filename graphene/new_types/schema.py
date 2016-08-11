import inspect

from graphql import GraphQLSchema, graphql
from graphql.utils.introspection_query import introspection_query
from graphql.utils.schema_printer import print_schema


from .objecttype import ObjectType
# from ..utils.get_graphql_type import get_graphql_type


# from graphql.type.schema import assert_object_implements_interface

# from collections import defaultdict


class Schema(GraphQLSchema):

    def __init__(self, query=None, mutation=None, subscription=None, directives=None, types=None, executor=None):
        self._query = query
        self._mutation = mutation
        self._subscription = subscription
        self.types = types
        self._executor = executor
        # super(Schema, self).__init__(
        #     query=query,
        #     mutation=mutation,
        #     subscription=subscription,
        #     directives=directives,
        #     types=self.types
        # )

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
        self.types.append(object_type)

    def introspect(self):
        return self.execute(introspection_query).data

    def __str__(self):
        return print_schema(self)

    def lazy(self, _type):
        return lambda: self.get_type(_type)

    def _type_map_reducer(self, map, type):
        if not type:
            return map
        if inspect.isclass(type) and issubclass(type, (ObjectType)):
            return self._type_map_reducer_graphene(map, type)
        return super(Schema, self)._type_map_reducer(map, type)

    def _type_map_reducer_graphene(self, map, type):
        # from .structures import List, NonNull
        return map

    # def rebuild(self):
    #     self._possible_type_map = defaultdict(set)
    #     self._type_map = self._build_type_map(self.types)
    #     # Keep track of all implementations by interface name.
    #     self._implementations = defaultdict(list)
    #     for type in self._type_map.values():
    #         if isinstance(type, GraphQLObjectType):
    #             for interface in type.get_interfaces():
    #                 self._implementations[interface.name].append(type)

    #     # Enforce correct interface implementations.
    #     for type in self._type_map.values():
    #         if isinstance(type, GraphQLObjectType):
    #             for interface in type.get_interfaces():
    #                 assert_object_implements_interface(self, type, interface)
