from pytest import mark

from graphene import ObjectType, Int, String, Schema, Field


class Query(ObjectType):
    hello = String()

    def resolve_hello(root, info):
        return "Hello, world!"


class Subscription(ObjectType):
    count_to_ten = Field(Int)

    async def subscribe_count_to_ten(root, info):
        count = 0
        while count < 10:
            count += 1
            yield count


schema = Schema(query=Query, subscription=Subscription)


@mark.asyncio
async def test_subscription():
    subscription = "subscription { countToTen }"
    result = await schema.subscribe(subscription)
    count = 0
    async for item in result:
        count = item.data["countToTen"]
    assert count == 10


@mark.asyncio
async def test_subscription_fails_with_invalid_query():
    # It fails if the provided query is invalid
    subscription = "subscription { "
    result = await schema.subscribe(subscription)
    assert not result.data
    assert result.errors
    assert "Syntax Error: Expected Name, found <EOF>" in str(result.errors[0])


@mark.asyncio
async def test_subscription_fails_when_query_is_not_valid():
    # It can't subscribe to two fields at the same time, triggering a
    # validation error.
    subscription = "subscription { countToTen, b: countToTen }"
    result = await schema.subscribe(subscription)
    assert not result.data
    assert result.errors
    assert "Anonymous Subscription must select only one top level field." in str(
        result.errors[0]
    )
