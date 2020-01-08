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
            yield {"count_to_ten": count}


schema = Schema(query=Query, subscription=Subscription)


@mark.asyncio
async def test_subscription():
    subscription = "subscription { countToTen }"
    result = await schema.subscribe(subscription)
    count = 0
    async for item in result:
        count = item.data["countToTen"]
    assert count == 10
