|Graphene Logo| `Graphene <http://graphene-python.org>`__ |Build Status| |PyPI version| |Coverage Status|
=========================================================================================================

Graphene is a Python library for building GraphQL schemas/types fast and
easily. \* **Easy to use:** Graphene helps you use GraphQL in Python
without effort. \* **Relay:** Graphene has builtin support for Relay \*
**Django:** Automatic *Django model* mapping to Graphene Types. *See an
`example Django <http://github.com/graphql-python/swapi-graphene>`__
implementation*

*But, what is supported in this Python version?* **Everything**:
Interfaces, ObjectTypes, Mutations and Relay (Nodes, Connections and
Mutations).

Installation
------------

For instaling graphene, just run this command in your shell

.. code:: bash

    pip install graphene
    # Or in case of need Django model support
    pip install graphene[django]

Examples
--------

Here is one example for get you started:

.. code:: python

    class Query(graphene.ObjectType):
        hello = graphene.StringField(description='A typical hello world')
        ping = graphene.StringField(description='Ping someone',
                                    to=graphene.Argument(graphene.String))

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
          ping(to:'peter')
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
