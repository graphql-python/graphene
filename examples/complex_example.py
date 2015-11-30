import graphene


class GeoInput(graphene.InputObjectType):
    lat = graphene.Float(required=True)
    lng = graphene.Float(required=True)


class Address(graphene.ObjectType):
    latlng = graphene.String()


class Query(graphene.ObjectType):
    address = graphene.Field(Address, geo=graphene.Argument(GeoInput))

    def resolve_address(self, args, info):
        geo = args.get('geo')
        return Address(latlng="({},{})".format(geo.get('lat'), geo.get('lng')))


schema = graphene.Schema(query=Query)
query = '''
    query something{
      address(geo: {lat:32.2, lng:12}) {
        latlng
      }
    }
'''

result = schema.execute(query)
print(result.data['address']['latlng'])
