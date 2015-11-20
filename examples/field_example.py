import graphene


class Person(graphene.Interface):
    name = graphene.String()
    age = graphene.ID()


class Patron(Person):
    id = graphene.ID()


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
# Print the result
print(result.data['patron'])
