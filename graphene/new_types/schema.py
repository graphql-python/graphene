import inspect

from graphql import GraphQLSchema, graphql
from graphql.utils.introspection_query import introspection_query
from graphql.utils.schema_printer import print_schema


from .objecttype import ObjectType
from .scalars import Scalar
# from ..utils.get_graphql_type import get_graphql_type


# from graphql.type.schema import assert_object_implements_interface

# from collections import defaultdict


from collections import Iterable, OrderedDict, defaultdict
from functools import reduce

from graphql.utils.type_comparators import is_equal_type, is_type_sub_type_of
from graphql.type.definition import (GraphQLInputObjectType, GraphQLInterfaceType, GraphQLField,
                         GraphQLList, GraphQLNonNull, GraphQLObjectType,
                         GraphQLUnionType)
from graphql.type.directives import (GraphQLDirective, GraphQLIncludeDirective,
                         GraphQLSkipDirective)
from graphql.type.introspection import IntrospectionSchema
from graphql.type.schema import assert_object_implements_interface


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
        self._possible_type_map = defaultdict(set)
        self._type_map = self._build_type_map(types)
        # Keep track of all implementations by interface name.
        self._implementations = defaultdict(list)
        for type in self._type_map.values():
            if isinstance(type, GraphQLObjectType):
                for interface in type.get_interfaces():
                    self._implementations[interface.name].append(type)

        # Enforce correct interface implementations.
        for type in self._type_map.values():
            if isinstance(type, GraphQLObjectType):
                for interface in type.get_interfaces():
                    assert_object_implements_interface(self, type, interface)

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
        if inspect.isclass(type) and issubclass(type, (ObjectType, Scalar)):
            return self._type_map_reducer_graphene(map, type)
        return super(Schema, self)._type_map_reducer(map, type)

    def _type_map_reducer_graphene(self, map, type):
        # from .structures import List, NonNull
        from ..generators.definitions import GrapheneObjectType
        if issubclass(type, ObjectType):
            fields = OrderedDict()
            for name, field in type._meta.fields.items():
                map = self._type_map_reducer(map, field.type)
                field_type = map.get(field.type._meta.name)
                _field = GraphQLField(
                    field_type,
                    args=field.args,
                    resolver=field.resolver,
                    deprecation_reason=field.deprecation_reason,
                    description=field.description
                )
                fields[name] = _field
            map[type._meta.name] = GrapheneObjectType(
                graphene_type=type,
                name=type._meta.name,
                description=type._meta.description,
                fields=fields,
                is_type_of=type.is_type_of,
                interfaces=type._meta.interfaces
            )
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
