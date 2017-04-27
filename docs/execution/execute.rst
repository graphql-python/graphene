Executing a query
=================


For executing a query a schema, you can directly call the ``execute`` method on it.


.. code:: python

    schema = graphene.Schema(...)
    result = schema.execute('{ name }')

``result`` represents the result of execution. ``result.data`` is the result of executing the query, ``result.errors`` is ``None`` if no errors occurred, and is a non-empty list if an error occurred.


Context
_______

You can pass context to a query via ``context_value``.


.. code:: python

    class Query(graphene.ObjectType):
        name = graphene.String()

        def resolve_name(self, args, context, info):
            return context.get('name')

    schema = graphene.Schema(Query)
    result = schema.execute('{ name }', context_value={'name': 'Syrus'})

