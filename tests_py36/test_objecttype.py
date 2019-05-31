from graphene import Schema, ObjectType, String


def test_objecttype_meta_with_annotations():
    class Query(ObjectType):
        class Meta:
            name: str = 'oops'

        hello = String()

        def resolve_hello(self, info):
            return 'Hello'

    schema = Schema(query=Query)
    assert schema is not None
