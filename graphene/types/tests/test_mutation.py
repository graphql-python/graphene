import pytest

from ..mutation import Mutation
from ..objecttype import ObjectType


def test_generate_mutation_no_args():
    class MyMutation(Mutation):
        '''Documentation'''
        @classmethod
        def mutate(cls, *args, **kwargs):
            pass

    assert issubclass(MyMutation, ObjectType)
    assert MyMutation._meta.name == "MyMutation"
    assert MyMutation._meta.description == "Documentation"
    assert MyMutation.Field().resolver == MyMutation.mutate


# def test_generate_mutation_with_args():
#     class MyMutation(Mutation):
#         '''Documentation'''
#         class Input:
#             s = String()

#         @classmethod
#         def mutate(cls, *args, **kwargs):
#             pass

#     graphql_type = MyMutation._meta.graphql_type
#     field = MyMutation.Field()
#     assert graphql_type.name == "MyMutation"
#     assert graphql_type.description == "Documentation"
#     assert isinstance(field, Field)
#     assert field.type == MyMutation._meta.graphql_type
#     assert 's' in field.args
#     assert field.args['s'].type == String


def test_generate_mutation_with_meta():
    class MyMutation(Mutation):

        class Meta:
            name = 'MyOtherMutation'
            description = 'Documentation'

        @classmethod
        def mutate(cls, *args, **kwargs):
            pass

    assert MyMutation._meta.name == "MyOtherMutation"
    assert MyMutation._meta.description == "Documentation"
    assert MyMutation.Field().resolver == MyMutation.mutate


def test_mutation_raises_exception_if_no_mutate():
    with pytest.raises(AssertionError) as excinfo:
        class MyMutation(Mutation):
            pass

    assert "All mutations must define a mutate method in it" == str(excinfo.value)
