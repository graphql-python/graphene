import graphene


class User(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()


class Query(graphene.ObjectType):
    me = graphene.Field(User)

    @graphene.annotate(context=graphene.Context)
    def resolve_me(self, context):
        return context['user']


schema = graphene.Schema(query=Query)
query = '''
    query something{
      me {
        id
        name
      }
    }
'''


def test_query():
    result = schema.execute(query, context_value={'user': User(id='1', name='Syrus')})
    assert not result.errors
    assert result.data == {
        'me': {
            'id': '1',
            'name': 'Syrus',
        }
    }


if __name__ == '__main__':
    result = schema.execute(query, context_value={'user': User(id='X', name='Console')})
    print(result.data['me'])
