import graphene
from py.test import raises
from graphene.core.schema import Schema

my_id = 0


class Query(graphene.ObjectType):
    base = graphene.StringField()


class ChangeNumber(graphene.Mutation):
    '''Result mutation'''
    class Input:
        id = graphene.IntField(required=True)

    result = graphene.StringField()

    @classmethod
    def mutate(cls, instance, args, info):
        global my_id
        my_id = my_id + 1
        return ChangeNumber(result=my_id)


class MyResultMutation(graphene.ObjectType):
    change_number = graphene.Field(ChangeNumber)


schema = Schema(query=Query, mutation=MyResultMutation)


def test_mutate():
    query = '''
    mutation M{
      first: changeNumber {
        result
      },
      second: changeNumber {
        result
      }
    }
    '''
    expected = {
        'first': {
            'result': '1',
        },
        'second': {
            'result': '2',
        }
    }
    result = schema.execute(query, root=object())
    assert not result.errors
    assert result.data == expected
