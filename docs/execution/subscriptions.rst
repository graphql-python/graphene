.. _SchemaSubscription:

Subscriptions
=============

To create a subscription, you can directly call the ``subscribe`` method on the
schema. This method is async and must be awaited.

.. code:: python

    import asyncio
    from datetime import datetime
    from graphene import ObjectType, String, Schema, Field

    # Every schema requires a query.
    class Query(ObjectType):
        hello = String()

        def resolve_hello(root, info):
            return "Hello, world!"

    class Subscription(ObjectType):
        time_of_day = String()

        async def subscribe_time_of_day(root, info):
            while True:
                yield datetime.now().isoformat()
                await asyncio.sleep(1)

    schema = Schema(query=Query, subscription=Subscription)

    async def main(schema):
        subscription = 'subscription { timeOfDay }'
        result = await schema.subscribe(subscription)
        async for item in result:
            print(item.data['timeOfDay'])

    asyncio.run(main(schema))

The ``result`` is an async iterator which yields items in the same manner as a query.
