.. _SchemaExecute:

Executing a query
=================


For executing a query against a schema, you can directly call the ``execute`` method on it.


.. code:: python

    from graphene import Schema

    schema = Schema(...)
    result = schema.execute('{ name }')

``result`` represents the result of execution. ``result.data`` is the result of executing the query, ``result.errors`` is ``None`` if no errors occurred, and is a non-empty list if an error occurred.


For executing a subscription, you can directly call the ``subscribe`` method on it.
This method is async and must be awaited.

.. code:: python

    import asyncio
    from datetime import datetime
    from graphene import ObjectType, String, Schema, Field

    # All schema require a query.
    class Query(ObjectType):
        hello = String()

        def resolve_hello(root, info):
            return 'Hello, world!'

    class Subscription(ObjectType):
        time_of_day = Field(String)

        async def subscribe_time_of_day(root, info):
            while True:
                yield { 'time_of_day': datetime.now().isoformat()}
                await asyncio.sleep(1)

    SCHEMA = Schema(query=Query, subscription=Subscription)

    async def main(schema):

        subscription = 'subscription { timeOfDay }'
        result = await schema.subscribe(subscription)
        async for item in result:
            print(item.data['timeOfDay'])

    asyncio.run(main(SCHEMA))

The ``result`` is an async iterator which yields items in the same manner as a query.

.. _SchemaExecuteContext:

Context
_______

You can pass context to a query via ``context``.


.. code:: python

    from graphene import ObjectType, String, Schema

    class Query(ObjectType):
        name = String()

        def resolve_name(root, info):
            return info.context.get('name')

    schema = Schema(Query)
    result = schema.execute('{ name }', context={'name': 'Syrus'})
    assert result.data['name'] == 'Syrus'


Variables
_________

You can pass variables to a query via ``variables``.


.. code:: python

    from graphene import ObjectType, Field, ID, Schema

    class Query(ObjectType):
        user = Field(User, id=ID(required=True))

        def resolve_user(root, info, id):
            return get_user_by_id(id)

    schema = Schema(Query)
    result = schema.execute(
        '''
          query getUser($id: ID) {
            user(id: $id) {
              id
              firstName
              lastName
            }
          }
        ''',
        variables={'id': 12},
    )

Root Value
__________

Value used for :ref:`ResolverParamParent` in root queries and mutations can be overridden using ``root`` parameter.

.. code:: python

    from graphene import ObjectType, Field, Schema

    class Query(ObjectType):
        me = Field(User)

        def resolve_user(root, info):
            return {'id': root.id, 'firstName': root.name}

    schema = Schema(Query)
    user_root = User(id=12, name='bob'}
    result = schema.execute(
        '''
        query getUser {
            user {
                id
                firstName
                lastName
            }
        }
        ''',
        root=user_root
    )
    assert result.data['user']['id'] == user_root.id

Operation Name
______________

If there are multiple operations defined in a query string, ``operation_name`` should be used to indicate which should be executed.

.. code:: python

    from graphene import ObjectType, Field, Schema

    class Query(ObjectType):
        me = Field(User)

        def resolve_user(root, info):
            return get_user_by_id(12)

    schema = Schema(Query)
    query_string = '''
        query getUserWithFirstName {
            user {
                id
                firstName
                lastName
            }
        }
        query getUserWithFullName {
            user {
                id
                fullName
            }
        }
    '''
    result = schema.execute(
        query_string,
        operation_name='getUserWithFullName'
    )
    assert result.data['user']['fullName']
