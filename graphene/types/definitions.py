from enum import Enum as PyEnum

from graphql import (
    GraphQLEnumType,
    GraphQLInputObjectType,
    GraphQLInterfaceType,
    GraphQLObjectType,
    GraphQLScalarType,
    GraphQLUnionType,
)


class GrapheneGraphQLType:
    """
    A class for extending the base GraphQLType with the related
    graphene_type
    """

    def __init__(self, *args, **kwargs):
        self.graphene_type = kwargs.pop("graphene_type")
        super(GrapheneGraphQLType, self).__init__(*args, **kwargs)


class GrapheneInterfaceType(GrapheneGraphQLType, GraphQLInterfaceType):
    pass


class GrapheneUnionType(GrapheneGraphQLType, GraphQLUnionType):
    pass


class GrapheneObjectType(GrapheneGraphQLType, GraphQLObjectType):
    pass


class GrapheneScalarType(GrapheneGraphQLType, GraphQLScalarType):
    pass


class GrapheneEnumType(GrapheneGraphQLType, GraphQLEnumType):
    def serialize(self, value):
        if not isinstance(value, PyEnum):
            enum = self.graphene_type._meta.enum
            try:
                # Try and get enum by value
                value = enum(value)
            except ValueError:
                # Try ang get enum by name
                value = enum[value]
        return super(GrapheneEnumType, self).serialize(value)


class GrapheneInputObjectType(GrapheneGraphQLType, GraphQLInputObjectType):
    pass
