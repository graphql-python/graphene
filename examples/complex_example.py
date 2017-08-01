import graphene


class GeoInput(graphene.InputObjectType):
    lat = graphene.Float(required=True)
    lng = graphene.Float(required=True)


class Address(graphene.ObjectType):
    latlng = graphene.String()


class Query(graphene.ObjectType):
    address = graphene.Field(Address, geo=GeoInput(required=True))

    def resolve_address(self, info, geo):
        return Address(latlng="({},{})".format(geo.get('lat'), geo.get('lng')))


schema = graphene.Schema(query=Query)
query = '''
    query something{
      address(geo: {lat:32.2, lng:12}) {
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


if __name__ == '__main__':
    result = schema.execute(query)
    print(result.data['address']['latlng'])
