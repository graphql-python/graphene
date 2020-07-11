from pytest import mark

from graphene import ObjectType, Int, String, Schema
from graphene.types.objecttype import ObjectTypeOptions


MYPY = False
if MYPY:
    from typing import Callable  # NOQA


class Query(ObjectType):
    a = String()


class SubscriptionOptions(ObjectTypeOptions):
    pass


class Subscription(ObjectType):
    @classmethod
    def __init_subclass_with_meta__(
        cls, _meta=None, **options,
    ):
        if not _meta:
            _meta = SubscriptionOptions(cls)

        super().__init_subclass_with_meta__(_meta=_meta, **options)


class MySubscription(Subscription):
    count_to_ten = Int(yes=Int())

    async def subscribe_count_to_ten(root, info, **kwargs):
        count = 0
        while count < 10:
            count += 1
            yield count


schema = Schema(query=Query, subscription=MySubscription)


@mark.asyncio
async def test_subscription():
    subscription = """
        subscription {
            countToTen
        }
    """
    result = await schema.subscribe(subscription)
    count = 0
    async for item in result:
        count = item.data["countToTen"]
    assert count == 10
