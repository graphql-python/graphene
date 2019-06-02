from graphene import ObjectType, ID, String, Int, Field, Schema


class Patron(ObjectType):
    id = ID()
    name = String()
    age = Int()


class Query(ObjectType):

    patron = Field(Patron)

    def resolve_patron(self, info):
        return Patron(id=1, name="Syrus", age=27)


schema = Schema(query=Query)
query = """
    query something{
      patron {
        id
        name
        age
      }
    }
"""


def test_query():
    result = schema.execute(query)
    assert not result.errors
    assert result.data == {"patron": {"id": "1", "name": "Syrus", "age": 27}}


if __name__ == "__main__":
    result = schema.execute(query)
    print(result.data["patron"])
