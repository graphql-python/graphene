from pytest import mark

from graphene import ObjectType, Int, String, Schema
from graphene.types.objecttype import ObjectTypeOptions
from graphene.utils.get_unbound_function import get_unbound_function


class Query(ObjectType):
    a = String()


class SubscriptionOptions(ObjectTypeOptions):
    pass


class Subscription(ObjectType):
    @classmethod
    def __init_subclass_with_meta__(
        cls,
        resolver=None,
        _meta=None,
        **options,
    ):
        if not _meta:
            _meta = SubscriptionOptions(cls)

        if not resolver:
            subscribe = getattr(cls, "subscribe", None)
            assert subscribe, "The Subscribe class must define a subscribe method"
            resolver = get_unbound_function(subscribe)

        _meta.resolver = resolver

        super().__init_subclass_with_meta__(_meta=_meta, **options)


class MySubscription(Subscription):
    count_to_ten = Int()

    async def subscribe(root, info):
        count = 0
        while count < 10:
            count += 1
            yield {"count_to_ten": count}


schema = Schema(query=Query, subscription=MySubscription)


@mark.asyncio
async def test_subscription():
    subscription = "subscription { countToTen }"
    result = await schema.subscribe(subscription)
    count = 0
    async for item in result:
        count = item.data["countToTen"]
    assert count == 10
