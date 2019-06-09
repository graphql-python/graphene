.. _SchemaExecute:

Executing a query
=================


For executing a query a schema, you can directly call the ``execute`` method on it.


.. code:: python

    from graphene import Schema

    schema = Schema(...)
    result = schema.execute('{ name }')

``result`` represents the result of execution. ``result.data`` is the result of executing the query, ``result.errors`` is ``None`` if no errors occurred, and is a non-empty list if an error occurred.


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

Value used for :ref:`ResolverRootArgument` in root queries and mutations can be overridden using ``root`` parameter.

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
