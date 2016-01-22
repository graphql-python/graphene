import graphene


class Patron(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()
    age = graphene.ID()


class Query(graphene.ObjectType):

    patron = graphene.Field(Patron)

    def resolve_patron(self, args, info):
        return Patron(id=1, name='Demo')

schema = graphene.Schema(query=Query)
query = '''
    query something{
      patron {
        id
        name
      }
    }
'''
result = schema.execute(query)
print(result.data['patron'])
