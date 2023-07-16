# https://github.com/graphql-python/graphene/issues/1293

import datetime

import graphene
from graphql.utilities import print_schema


class Filters(graphene.InputObjectType):
    datetime_after = graphene.DateTime(
        required=False,
        default_value=datetime.datetime.utcfromtimestamp(1434549820776 / 1000),
    )
    datetime_before = graphene.DateTime(
        required=False,
        default_value=datetime.datetime.utcfromtimestamp(1444549820776 / 1000),
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


def test_print_schema():
    schema = graphene.Schema(query=Query, mutation=Mutations)
    schema_str = print_schema(schema.graphql_schema)
    assert schema_str, "non-empty schema printed"
