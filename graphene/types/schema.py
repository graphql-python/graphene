import inspect

from graphql import GraphQLSchema, graphql, is_type
from graphql.utils.introspection_query import introspection_query
from graphql.utils.schema_printer import print_schema


from .objecttype import ObjectType
from .structures import List, NonNull
from .scalars import Scalar, String
# from ..utils.get_graphql_type import get_graphql_type


# from graphql.type.schema import assert_object_implements_interface

# from collections import defaultdict


from graphql.type.directives import (GraphQLDirective, GraphQLIncludeDirective,
                                     GraphQLSkipDirective)
from graphql.type.introspection import IntrospectionSchema
from .typemap import TypeMap, is_graphene_type


class Schema(GraphQLSchema):

    def __init__(self, query=None, mutation=None, subscription=None, directives=None, types=None, executor=None):
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

        self._directives = directives
        initial_types = [
            query,
            mutation,
            subscription,
            IntrospectionSchema
        ]
        if types:
            initial_types += types
        self._type_map = TypeMap(initial_types)

    def get_query_type(self):
        return self.get_graphql_type(self._query)

    def get_mutation_type(self):
        return self.get_graphql_type(self._mutation)

    def get_subscription_type(self):
        return self.get_graphql_type(self._subscription)

    def get_graphql_type(self, _type):
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
