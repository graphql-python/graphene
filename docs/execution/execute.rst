.. _SchemaExecute:

Executing a query
=================


For executing a query a schema, you can directly call the ``execute`` method on it.


.. code:: python

    schema = graphene.Schema(...)
    result = schema.execute('{ name }')

``result`` represents the result of execution. ``result.data`` is the result of executing the query, ``result.errors`` is ``None`` if no errors occurred, and is a non-empty list if an error occurred.


.. _SchemaExecuteContext:

Context
_______

You can pass context to a query via ``context``.


.. code:: python

    class Query(graphene.ObjectType):
        name = graphene.String()

        def resolve_name(root, info):
            return info.context.get('name')

    schema = graphene.Schema(Query)
    result = schema.execute('{ name }', context={'name': 'Syrus'})



Variables
_________

You can pass variables to a query via ``variables``.


.. code:: python

    class Query(graphene.ObjectType):
        user = graphene.Field(User, id=graphene.ID(required=True))

        def resolve_user(root, info, id):
            return get_user_by_id(id)

    schema = graphene.Schema(Query)
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

Value used for :ref:`ResolverRootArgument` in root queries and mutations can be overridden using ``root`` parameter.

.. code:: python

    class Query(graphene.ObjectType):
        me = graphene.Field(User)

        def resolve_user(root, info):
            return get_user_by_id(root.id)

    schema = graphene.Schema(Query)
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

Operation Name
______________

If there are multiple operations defined in a query string, ``operation_name`` should be used to indicate which should be executed.

.. code:: python

    class Query(graphene.ObjectType):
        me = graphene.Field(User)

        def resolve_user(root, info):
            return get_user_by_id(12)

    schema = graphene.Schema(Query)
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
                firstName
                lastName
            }
        }
    '''
    result = schema.execute(
        query_string,
        operation_name='getUserWithFullName'
    )
