import pytest

from ...types import ObjectType, Schema
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

    assert "MyMutation.mutate_and_get_payload method is required in a ClientIDMutation ObjectType." == str(
        excinfo.value)


def test_node_good():
    graphql_type = SaySomething._meta.graphql_type
    fields = graphql_type.get_fields()
    assert 'phrase' in fields
    graphql_field = SaySomething.Field()
    assert graphql_field.type == SaySomething._meta.graphql_type
    assert 'input' in graphql_field.args
    input = graphql_field.args['input']
    assert 'clientMutationId' in input.type.of_type.get_fields()


def test_node_query():
    executed = schema.execute(
        'mutation a { say(input: {what:"hello", clientMutationId:"1"}) { phrase } }'
    )
    assert not executed.errors
    assert executed.data == {'say': {'phrase': 'hello'}}
