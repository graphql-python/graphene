
from graphql.type import GraphQLObjectType

from graphene.core.schema import Schema
from graphene.core.types import String

from ...types.argument import ArgumentsGroup
from ..mutation import Mutation


def test_mutation():
    class MyMutation(Mutation):
        '''MyMutation description'''
        class Input:
            arg_name = String()
        name = String()

    schema = Schema()

    object_type = schema.T(MyMutation)
    assert MyMutation._meta.type_name == 'MyMutation'
    assert isinstance(object_type, GraphQLObjectType)
    assert object_type.description == 'MyMutation description'
    assert list(object_type.get_fields().keys()) == ['name']
    assert MyMutation._meta.fields_map['name'].object_type == MyMutation
    assert isinstance(MyMutation.arguments, ArgumentsGroup)
    assert 'argName' in schema.T(MyMutation.arguments)
