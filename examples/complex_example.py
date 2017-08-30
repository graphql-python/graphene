import graphene


class GeoInput(graphene.InputObjectType):
    lat = graphene.Float(required=True)
    lng = graphene.Float(required=True)

    @property
    def latlng(self):
        return "({},{})".format(self.lat, self.lng)


class Address(graphene.ObjectType):
    latlng = graphene.String()


class Query(graphene.ObjectType):
    address = graphene.Field(Address, geo=GeoInput(required=True))

    def resolve_address(self, info, geo):
        return Address(latlng=geo.latlng)


class CreateAddress(graphene.Mutation):
    
    class Arguments:
        geo = GeoInput(required=True)

    Output = Address

    def mutate(self, info, geo):
        return Address(latlng=geo.latlng)


class Mutation(graphene.ObjectType):
    create_address = CreateAddress.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
query = '''
    query something{
      address(geo: {lat:32.2, lng:12}) {
        latlng
      }
    }
'''
mutation = '''
    mutation addAddress{
      createAddress(geo: {lat:32.2, lng:12}) {
        latlng
      }
    }
'''


def test_query():
    result = schema.execute(query)
    assert not result.errors
    assert result.data == {
        'address': {
            'latlng': "(32.2,12.0)",
        }
    }


def test_mutation():
    result = schema.execute(mutation)
    assert not result.errors
    assert result.data == {
        'createAddress': {
            'latlng': "(32.2,12.0)",
        }
    }


if __name__ == '__main__':
    result = schema.execute(query)
    print(result.data['address']['latlng'])
