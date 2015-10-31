import graphene
from graphene import relay
from graphene.core.schema import Schema
from graphene.core.types import InputObjectType
from graphql.core.type import GraphQLInputObjectField

my_id = 0


class Query(graphene.ObjectType):
    base = graphene.StringField()


class ChangeNumber(relay.ClientIDMutation):
    '''Result mutation'''
    class Input:
        to = graphene.IntField()

    result = graphene.StringField()

    @classmethod
    def mutate_and_get_payload(cls, input, info):
        global my_id
        my_id = input.get('to', my_id + 1)
        return ChangeNumber(result=my_id)


class MyResultMutation(graphene.ObjectType):
    change_number = graphene.Field(ChangeNumber)


schema = Schema(query=Query, mutation=MyResultMutation)


def test_mutation_input():
    assert ChangeNumber.input_type
    assert ChangeNumber.input_type._meta.type_name == 'ChangeNumberInput'
    assert list(ChangeNumber.input_type._meta.fields_map.keys()) == ['input']
    _input = ChangeNumber.input_type._meta.fields_map['input']
    inner_type = _input.get_object_type(schema)
    client_mutation_id_field = inner_type._meta.fields_map[
        'client_mutation_id']
    assert issubclass(inner_type, InputObjectType)
    assert isinstance(client_mutation_id_field, graphene.StringField)
    assert client_mutation_id_field.object_type == inner_type
    assert isinstance(client_mutation_id_field.internal_field(
        schema), GraphQLInputObjectField)


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
