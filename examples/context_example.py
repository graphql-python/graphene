from graphene import ObjectType, ID, String, Field, Schema


class User(ObjectType):
    id = ID()
    name = String()


class Query(ObjectType):
    me = Field(User)

    def resolve_me(self, info):
        return info.context["user"]


schema = Schema(query=Query)
query = """
    query something{
      me {
        id
        name
      }
    }
"""


def test_query():
    result = schema.execute(query, context={"user": User(id="1", name="Syrus")})
    assert not result.errors
    assert result.data == {"me": {"id": "1", "name": "Syrus"}}


if __name__ == "__main__":
    result = schema.execute(query, context={"user": User(id="X", name="Console")})
    print(result.data["me"])
