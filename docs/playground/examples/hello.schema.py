import graphene

class Query(graphene.ObjectType):
    hello = graphene.String()
    ping = graphene.String(to=graphene.String())

    def resolve_hello(self, args, context, info):
        return 'World'

    def resolve_ping(self, args, context, info):
        return 'Pinging {}'.format(args.get('to'))

schema = graphene.Schema(query=Query)
