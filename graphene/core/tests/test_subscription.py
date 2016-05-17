import graphene


class Query(graphene.ObjectType):
    base = graphene.String()


class Subscription(graphene.ObjectType):
    subscribe_to_foo = graphene.Boolean(id=graphene.Int())

    def resolve_subscribe_to_foo(self, args, context, info):
        return args.get('id') == 1


schema = graphene.Schema(query=Query, subscription=Subscription)


def test_execute_subscription():
    query = '''
    subscription {
      subscribeToFoo(id: 1)
    }
    '''
    expected = {
        'subscribeToFoo': True
    }
    result = schema.execute(query)
    assert not result.errors
    assert result.data == expected
