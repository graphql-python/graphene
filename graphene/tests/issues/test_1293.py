# https://github.com/graphql-python/graphene/issues/1293

from datetime import datetime, timezone

import graphene
from graphql.utilities import print_schema


class Filters(graphene.InputObjectType):
    datetime_after = graphene.DateTime(
        required=False,
        default_value=datetime.fromtimestamp(1434549820.776, timezone.utc),
    )
    datetime_before = graphene.DateTime(
        required=False,
        default_value=datetime.fromtimestamp(1444549820.776, timezone.utc),
    )


class SetDatetime(graphene.Mutation):
    class Arguments:
        filters = Filters(required=True)

    ok = graphene.Boolean()

    def mutate(root, info, filters):
        return SetDatetime(ok=True)


class Query(graphene.ObjectType):
    goodbye = graphene.String()


class Mutations(graphene.ObjectType):
    set_datetime = SetDatetime.Field()


def test_schema_printable_with_default_datetime_value():
    schema = graphene.Schema(query=Query, mutation=Mutations)
    schema_str = print_schema(schema.graphql_schema)
    assert schema_str, "empty schema printed"
