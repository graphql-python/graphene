from graphql.core.type.definition import GraphQLScalarType


def skip(value):
    return None

GraphQLSkipField = GraphQLScalarType(name='SkipField',
                                     serialize=skip,
                                     parse_value=skip,
                                     parse_literal=skip)
