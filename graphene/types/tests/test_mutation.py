import pytest

from graphql import GraphQLObjectType, GraphQLString

from ..field import Field
from ..mutation import Mutation
from ..objecttype import ObjectType
from ..scalars import String


def test_generate_mutation_no_args():
    class MyMutation(Mutation):
        '''Documentation'''
        @classmethod
        def mutate(cls, *args, **kwargs):
            pass

    assert issubclass(MyMutation, ObjectType)
    graphql_type = MyMutation._meta.graphql_type
    assert isinstance(graphql_type, GraphQLObjectType)
    assert graphql_type.name == "MyMutation"
    assert graphql_type.description == "Documentation"


def test_generate_mutation_with_args():
    class MyMutation(Mutation):
        '''Documentation'''
        class Input:
            s = String()

        @classmethod
        def mutate(cls, *args, **kwargs):
            pass

    graphql_type = MyMutation._meta.graphql_type
    field = MyMutation.Field()
    assert isinstance(graphql_type, GraphQLObjectType)
    assert graphql_type.name == "MyMutation"
    assert graphql_type.description == "Documentation"
    assert isinstance(field, Field)
    assert field.type == MyMutation._meta.graphql_type
    assert 's' in field.args
    assert field.args['s'].type == GraphQLString


def test_generate_mutation_with_meta():
    class MyMutation(Mutation):

        class Meta:
            name = 'MyOtherMutation'
            description = 'Documentation'

        @classmethod
        def mutate(cls, *args, **kwargs):
            pass

    graphql_type = MyMutation._meta.graphql_type
    assert isinstance(graphql_type, GraphQLObjectType)
    assert graphql_type.name == "MyOtherMutation"
    assert graphql_type.description == "Documentation"


def test_empty_mutation_has_meta():
    class MyMutation(Mutation):

        @classmethod
        def mutate(cls, *args, **kwargs):
            pass

    assert MyMutation._meta


def test_mutation_raises_exception_if_no_mutate():
    with pytest.raises(AssertionError) as excinfo:
        class MyMutation(Mutation):
            pass

    assert "All mutations must define a mutate method in it" == str(excinfo.value)
