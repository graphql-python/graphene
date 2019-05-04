import inspect

from graphql import GraphQLObjectType, GraphQLSchema, graphql, is_type
from graphql.type.directives import (
    GraphQLDirective,
    GraphQLIncludeDirective,
    GraphQLSkipDirective,
)
from graphql.type.introspection import introspection_types
from graphql.utilities.introspection_query import get_introspection_query
from graphql.utilities.schema_printer import print_schema

from .definitions import GrapheneGraphQLType
from .objecttype import ObjectType
from .typemap import is_graphene_type


def assert_valid_root_type(_type):
    if _type is None:
        return
    is_graphene_objecttype = inspect.isclass(_type) and issubclass(_type, ObjectType)
    is_graphql_objecttype = isinstance(_type, GraphQLObjectType)
    assert is_graphene_objecttype or is_graphql_objecttype, (
        "Type {} is not a valid ObjectType."
    ).format(_type)


Schema = GraphQLSchema

