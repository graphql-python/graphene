import inspect

from graphql import GraphQLSchema, graphql
from graphql.utils.introspection_query import introspection_query
from graphql.utils.schema_printer import print_schema


from .objecttype import ObjectType
from .structures import List, NonNull
from .scalars import Scalar, String
# from ..utils.get_graphql_type import get_graphql_type


# from graphql.type.schema import assert_object_implements_interface

# from collections import defaultdict


from collections import Iterable, OrderedDict, defaultdict
from functools import reduce

from graphql.utils.type_comparators import is_equal_type, is_type_sub_type_of
from graphql.type.definition import (GraphQLInputObjectType, GraphQLInterfaceType, GraphQLField,GraphQLScalarType,
                         GraphQLList, GraphQLNonNull, GraphQLObjectType,
                         GraphQLUnionType)
from graphql.type.directives import (GraphQLDirective, GraphQLIncludeDirective,
                         GraphQLSkipDirective)
from graphql.type.introspection import IntrospectionSchema
from graphql.type.schema import assert_object_implements_interface
from graphql.type.scalars import GraphQLString


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
        if isinstance(type, List) or (inspect.isclass(type) and issubclass(type, (ObjectType, Scalar))):
            return self._type_map_reducer_graphene(map, type)
        return super(Schema, self)._type_map_reducer(map, type)

    def _type_map_reducer_graphene(self, map, type):
        # from .structures import List, NonNull
        from ..generators.definitions import GrapheneObjectType, GrapheneScalarType
        if isinstance(type, List):
            return self._type_map_reducer(map, type.of_type)
        if issubclass(type, String):
            map[type._meta.name] = GraphQLString
            return map

        if type._meta.name in map:
            assert map[type._meta.name].graphene_type == type
            return map
        if issubclass(type, ObjectType):
            fields = OrderedDict()
            map[type._meta.name] = GrapheneObjectType(
                graphene_type=type,
                name=type._meta.name,
                description=type._meta.description,
                fields={},
                is_type_of=type.is_type_of,
                interfaces=type._meta.interfaces
            )
            for name, field in type._meta.fields.items():
                map = self._type_map_reducer(map, field.type)
                field_type = self.get_field_type(map, field.type)
                _field = GraphQLField(
                    field_type,
                    args=field.args,
                    resolver=field.resolver,
                    deprecation_reason=field.deprecation_reason,
                    description=field.description
                )
                fields[name] = _field
            map[type._meta.name].fields = fields
            # map[type._meta.name] = GrapheneScalarType(
            #     graphene_type=type,
            #     name=type._meta.name,
            #     description=type._meta.description,

            #     serialize=getattr(type, 'serialize', None),
            #     parse_value=getattr(type, 'parse_value', None),
            #     parse_literal=getattr(type, 'parse_literal', None),
            # )
        return map

    def get_field_type(self, map, type):
        if isinstance(type, List):
            return GraphQLList(self.get_field_type(map, type.of_type))
        return map.get(type._meta.name)
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
