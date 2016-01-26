|Graphene Logo| `Graphene <http://graphene-python.org>`__ |Build Status| |PyPI version| |Coverage Status|
=========================================================================================================

`Graphene <http://graphene-python.org>`__ is a Python library for
building GraphQL schemas/types fast and easily.

-  **Easy to use:** Graphene helps you use GraphQL in Python without
   effort.
-  **Relay:** Graphene has builtin support for Relay
-  **Django:** Automatic *Django model* mapping to Graphene Types. Check
   a fully working
   `Django <http://github.com/graphql-python/swapi-graphene>`__
   implementation

Graphene also supports *SQLAlchemy*!

*What is supported in this Python version?* **Everything**: Interfaces,
ObjectTypes, Scalars, Unions and Relay (Nodes, Connections), in addition
to queries, mutations and subscriptions.

**NEW**!: `Try graphene
online <http://graphene-python.org/playground/>`__

Installation
------------

For instaling graphene, just run this command in your shell

.. code:: bash

    pip install graphene
    # In case of need Django model support
    pip install graphene[django]
    # Or in case of need SQLAlchemy support
    pip install graphene[sqlalchemy]

Examples
--------

Here is one example for get you started:

.. code:: python

    class Query(graphene.ObjectType):
        hello = graphene.String(description='A typical hello world')
        ping = graphene.String(description='Ping someone',
                               to=graphene.String())

        def resolve_hello(self, args, info):
            return 'World'

        def resolve_ping(self, args, info):
            return 'Pinging {}'.format(args.get('to'))

    schema = graphene.Schema(query=Query)

Then Querying ``graphene.Schema`` is as simple as:

.. code:: python

    query = '''
        query SayHello {
          hello
          ping(to:"peter")
        }
    '''
    result = schema.execute(query)

If you want to learn even more, you can also check the following
`examples <examples/>`__:

-  **Basic Schema**: `Starwars example <examples/starwars>`__
-  **Relay Schema**: `Starwars Relay
   example <examples/starwars_relay>`__
-  **Django model mapping**: `Starwars Django
   example <examples/starwars_django>`__
-  **SQLAlchemy model mapping**: `Flask SQLAlchemy
   example <examples/flask_sqlalchemy>`__

Contributing
------------

After cloning this repo, ensure dependencies are installed by running:

.. code:: sh

    python setup.py install

After developing, the full test suite can be evaluated by running:

.. code:: sh

    python setup.py test # Use --pytest-args="-v -s" for verbose mode

.. |Graphene Logo| image:: http://graphene-python.org/favicon.png
.. |Build Status| image:: https://travis-ci.org/graphql-python/graphene.svg?branch=master
   :target: https://travis-ci.org/graphql-python/graphene
.. |PyPI version| image:: https://badge.fury.io/py/graphene.svg
   :target: https://badge.fury.io/py/graphene
.. |Coverage Status| image:: https://coveralls.io/repos/graphql-python/graphene/badge.svg?branch=master&service=github
   :target: https://coveralls.io/github/graphql-python/graphene?branch=master
