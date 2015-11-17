from graphql.core.type import GraphQLInputObjectField

import graphene
from graphene import relay
from graphene.core.schema import Schema

my_id = 0


class Query(graphene.ObjectType):
    base = graphene.String()


class ChangeNumber(relay.ClientIDMutation):
    '''Result mutation'''
    class Input:
        to = graphene.Int()

    result = graphene.String()

    @classmethod
    def mutate_and_get_payload(cls, input, info):
        global my_id
        my_id = input.get('to', my_id + 1)
        return ChangeNumber(result=my_id)


class MyResultMutation(graphene.ObjectType):
    change_number = graphene.Field(ChangeNumber)


schema = Schema(query=Query, mutation=MyResultMutation)


def test_mutation_arguments():
    assert ChangeNumber.arguments
    assert list(ChangeNumber.arguments) == ['input']
    assert 'input' in ChangeNumber.arguments
    inner_type = ChangeNumber.input_type
    client_mutation_id_field = inner_type._meta.fields_map[
        'client_mutation_id']
    assert issubclass(inner_type, graphene.InputObjectType)
    assert isinstance(client_mutation_id_field.type, graphene.NonNull)
    assert isinstance(client_mutation_id_field.type.of_type, graphene.String)
    assert client_mutation_id_field.object_type == inner_type
    assert isinstance(schema.T(client_mutation_id_field), GraphQLInputObjectField)


def test_execute_mutations():
    query = '''
    mutation M{
      first: changeNumber(input: {clientMutationId: "mutation1"}) {
        clientMutationId
        result
      },
      second: changeNumber(input: {clientMutationId: "mutation2"}) {
        clientMutationId
        result
      }
      third: changeNumber(input: {clientMutationId: "mutation3", to: 5}) {
        result
        clientMutationId
      }
    }
    '''
    expected = {
        'first': {
            'clientMutationId': 'mutation1',
            'result': '1',
        },
        'second': {
            'clientMutationId': 'mutation2',
            'result': '2',
        },
        'third': {
            'clientMutationId': 'mutation3',
            'result': '5',
        }
    }
    result = schema.execute(query, root=object())
    assert not result.errors
    assert result.data == expected
