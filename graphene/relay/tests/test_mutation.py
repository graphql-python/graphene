import pytest

from ...types import ObjectType, Schema, Field, InputField, InputObjectType, Argument
from ...types.scalars import String
from ..mutation import ClientIDMutation


class SaySomething(ClientIDMutation):

    class Input:
        what = String()
    phrase = String()

    @staticmethod
    def mutate_and_get_payload(args, context, info):
        what = args.get('what')
        return SaySomething(phrase=str(what))


class RootQuery(ObjectType):
    something = String()


class Mutation(ObjectType):
    say = SaySomething.Field()

schema = Schema(query=RootQuery, mutation=Mutation)


def test_no_mutate_and_get_payload():
    with pytest.raises(AssertionError) as excinfo:
        class MyMutation(ClientIDMutation):
            pass

    assert "MyMutation.mutate_and_get_payload method is required in a ClientIDMutation." == str(
        excinfo.value)


def test_mutation():
    fields = SaySomething._meta.fields
    assert list(fields.keys()) == ['phrase']
    assert isinstance(fields['phrase'], Field)
    field = SaySomething.Field()
    assert field.type == SaySomething
    assert list(field.args.keys()) == ['input']
    assert isinstance(field.args['input'], Argument)
    assert field.args['input'].type == SaySomething.Input


def test_mutation_input():
    Input = SaySomething.Input
    assert issubclass(Input, InputObjectType)
    fields = Input._meta.fields
    assert list(fields.keys()) == ['what', 'client_mutation_id']
    assert isinstance(fields['what'], InputField)
    assert fields['what'].type == String
    assert isinstance(fields['client_mutation_id'], InputField)
    assert fields['client_mutation_id'].type == String


# def test_node_query():
#     executed = schema.execute(
#         'mutation a { say(input: {what:"hello", clientMutationId:"1"}) { phrase } }'
#     )
#     assert not executed.errors
#     assert executed.data == {'say': {'phrase': 'hello'}}
