from collections import OrderedDict

from graphql.type import GraphQLEnumType, GraphQLEnumValue


def enum_to_graphql_enum(enumeration):
    return GraphQLEnumType(
        name=enumeration.__name__,
        values=OrderedDict([(it.name, GraphQLEnumValue(it.value))
                            for it in enumeration]),
        description=enumeration.__doc__
    )
