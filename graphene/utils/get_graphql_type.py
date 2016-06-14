from graphql.type.definition import is_type

from .is_graphene_type import is_graphene_type


def get_graphql_type(_type):
    if is_type(_type):
        return _type
    elif is_graphene_type(_type):
        return _type._meta.graphql_type

    raise Exception("Cannot get GraphQL type of {}.".format(_type))
