from collections import OrderedDict
import pytest

from graphql_relay import to_global_id

from ...types import (Argument, Field, InputField, InputObjectType, ObjectType,
                      Schema, AbstractType, NonNull)
from ...types.scalars import String
from ..mutation import ClientIDMutation
from ..node import GlobalID, Node


class SharedFields(AbstractType):
    shared = String()


class MyNode(ObjectType):

    class Meta:
        interfaces = (Node, )

    name = String()


class SaySomething(ClientIDMutation):

    class Input:
        what = String()

    phrase = String()
    my_node_id = GlobalID(parent_type=MyNode)

    @staticmethod
    def mutate_and_get_payload(args, context, info):
        what = args.get('what')
        return SaySomething(phrase=str(what), my_node_id=1)


class OtherMutation(ClientIDMutation):

    class Input(SharedFields):
        additional_field = String()

    name = String()

    @classmethod
    def mutate_and_get_payload(cls, args, context, info):
        shared = args.get('shared', '')
        additionalField = args.get('additionalField', '')
        return SaySomething(name=shared + additionalField)


class RootQuery(ObjectType):
    something = String()


class Mutation(ObjectType):
    say = SaySomething.Field()
    other = OtherMutation.Field()

schema = Schema(query=RootQuery, mutation=Mutation)


def test_no_mutate_and_get_payload():
    with pytest.raises(AssertionError) as excinfo:
        class MyMutation(ClientIDMutation):
            pass

    assert "MyMutation.mutate_and_get_payload method is required in a ClientIDMutation." == str(
        excinfo.value)


def test_mutation():
    fields = SaySomething._meta.fields
    assert list(fields.keys()) == ['phrase', 'my_node_id', 'client_mutation_id']
    assert isinstance(fields['phrase'], Field)
    assert isinstance(fields['my_node_id'], GlobalID)
    field = SaySomething.Field()
    assert field.type == SaySomething
    assert list(field.args.keys()) == ['input']
    assert isinstance(field.args['input'], Argument)
    assert isinstance(field.args['input'].type, NonNull)
    assert field.args['input'].type.of_type == SaySomething.Input


def test_mutation_input():
    Input = SaySomething.Input
    assert issubclass(Input, InputObjectType)
    fields = Input._meta.fields
    assert list(fields.keys()) == ['what', 'client_mutation_id']
    assert isinstance(fields['what'], InputField)
    assert fields['what'].type == String
    assert isinstance(fields['client_mutation_id'], InputField)
    assert fields['client_mutation_id'].type == String


def test_subclassed_mutation():
    fields = OtherMutation._meta.fields
    assert list(fields.keys()) == ['name', 'client_mutation_id']
    assert isinstance(fields['name'], Field)
    field = OtherMutation.Field()
    assert field.type == OtherMutation
    assert list(field.args.keys()) == ['input']
    assert isinstance(field.args['input'], Argument)
    assert isinstance(field.args['input'].type, NonNull)
    assert field.args['input'].type.of_type == OtherMutation.Input


def test_subclassed_mutation_input():
    Input = OtherMutation.Input
    assert issubclass(Input, InputObjectType)
    fields = Input._meta.fields
    assert list(fields.keys()) == ['shared', 'additional_field', 'client_mutation_id']
    assert isinstance(fields['shared'], InputField)
    assert fields['shared'].type == String
    assert isinstance(fields['additional_field'], InputField)
    assert fields['additional_field'].type == String
    assert isinstance(fields['client_mutation_id'], InputField)
    assert fields['client_mutation_id'].type == String


def test_node_query():
    executed = schema.execute(
        'mutation a { say(input: {what:"hello", clientMutationId:"1"}) { phrase, clientMutationId, myNodeId} }'
    )
    assert not executed.errors
    assert dict(executed.data) == {'say': {'myNodeId': to_global_id('MyNode', '1'), 'clientMutationId': '1', 'phrase': 'hello'}}
