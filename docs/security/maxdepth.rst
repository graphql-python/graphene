Depth limit Validator
=====================

By default, GraphQL queries can be arbitrarily deep. This can lead to a denial of service attack where a client can send
a deeply nested query that will take a long time to execute. For that, you must find a cycle in the graph and iterate
over.

Example
-------

For example a simple app that allows you to find your friends and their friends can lead to this query :

.. code:: graphql

    query {
      me {
        friends {
          friends {
            friends {
              friends {
                ...
                # dumping the whole database
              }
            }
          }
        }
      }
    }

This is not a common use case, your dev team will not do that in the first place. But as your endpoint is publicly
available, you can't be sure that someone will not try to do so.

Remediation
-----------

Graphene provides a depth limit validator that can be used to prevent this kind of attack. It can be configured to limit
the depth of all the queries or only some specific ones. The only required argument is ``max_depth`` which is the
maximum allowed depth for any operation in a GraphQL document. The other optional parameters are the following ones :

- ``ignore``: A list of patterns that, if matched stops recursive depth checking. It can be one of the following :
    - ``Callable : (dict[str, int]) -> bool``: A function that receives the current operation and returns a boolean.
    - ``Pattern``: A compiled regex pattern that is matched against the operation name.
    - ``str``: An operation name.
- ``callback: (dict[str, int]) -> None`` Called each time validation runs. Receives an Object which is a map of the depths for each operation.

Usage
-----

Here is an example of how you would implement depth-limiting on your schema.

.. code:: python

    from graphql import validate, parse
    from graphene import ObjectType, Schema, String
    from graphene.validation import depth_limit_validator


    class MyQuery(ObjectType):
        name = String(required=True)


    schema = Schema(query=MyQuery)

    # queries which have a depth more than 20
    # will not be executed.

    validation_errors = validate(
        schema=schema.graphql_schema,
        document_ast=parse('THE QUERY'),
        rules=(
            depth_limit_validator(
                max_depth=20
            ),
        )
    )
