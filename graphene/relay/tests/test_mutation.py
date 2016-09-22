import pytest

from ...types import (AbstractType, Argument, Field, InputField,
                      InputObjectType, NonNull, ObjectType, Schema)
from ...types.scalars import String
from ..mutation import ClientIDMutation
from ..node import Node


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

    @staticmethod
    def mutate_and_get_payload(args, context, info):
        what = args.get('what')
        return SaySomething(phrase=str(what))


class OtherMutation(ClientIDMutation):

    class Input(SharedFields):
        additional_field = String()

    name = String()
    my_node_edge = Field(MyNode.Connection.Edge)

    @classmethod
    def mutate_and_get_payload(cls, args, context, info):
        shared = args.get('shared', '')
        additionalField = args.get('additionalField', '')
        edge_type = MyNode.Connection.Edge
        return OtherMutation(name=shared + additionalField,
                             my_node_edge=edge_type(
                                 cursor='1', node=MyNode(name='name')))


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
    assert list(fields.keys()) == ['phrase', 'client_mutation_id']
    assert isinstance(fields['phrase'], Field)
    field = SaySomething.Field()
    assert field.type == SaySomething
    assert list(field.args.keys()) == ['input']
    assert isinstance(field.args['input'], Argument)
    assert isinstance(field.args['input'].type, NonNull)
    assert field.args['input'].type.of_type == SaySomething.Input
    assert isinstance(fields['client_mutation_id'], Field)
    assert fields['client_mutation_id'].name == 'clientMutationId'
    assert fields['client_mutation_id'].type == String


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
    assert list(fields.keys()) == ['name', 'my_node_edge', 'client_mutation_id']
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


# def test_node_query():
#     executed = schema.execute(
#         'mutation a { say(input: {what:"hello", clientMutationId:"1"}) { phrase } }'
#     )
#     assert not executed.errors
#     assert executed.data == {'say': {'phrase': 'hello'}}

def test_edge_query():
    executed = schema.execute(
        'mutation a { other(input: {clientMutationId:"1"}) { clientMutationId, myNodeEdge { cursor node { name }} } }'
    )
    assert not executed.errors
    assert dict(executed.data) == {'other': {'clientMutationId': '1', 'myNodeEdge': {'cursor': '1', 'node': {'name': 'name'}}}}
