Please read `UPGRADE-v1.0.md </UPGRADE-v1.0.md>`__ to learn how to
upgrade to Graphene ``1.0``.

--------------

|Graphene Logo| `Graphene <http://graphene-python.org>`__ |Build Status| |PyPI version| |Coverage Status|
=========================================================================================================

`Graphene <http://graphene-python.org>`__ is a Python library for
building GraphQL schemas/types fast and easily.

-  **Easy to use:** Graphene helps you use GraphQL in Python without
   effort.
-  **Relay:** Graphene has builtin support for both Relay.
-  **Data agnostic:** Graphene supports any kind of data source: SQL
   (Django, SQLAlchemy), NoSQL, custom Python objects, etc. We believe
   that by providing a complete API you could plug Graphene anywhere
   your data lives and make your data available through GraphQL.

Integrations
------------

Graphene has multiple integrations with different frameworks:

+---------------------+----------------------------------------------------------------------------------------------+
| integration         | Package                                                                                      |
+=====================+==============================================================================================+
| Django              | `graphene-django <https://github.com/graphql-python/graphene-django/>`__                     |
+---------------------+----------------------------------------------------------------------------------------------+
| SQLAlchemy          | `graphene-sqlalchemy <https://github.com/graphql-python/graphene-sqlalchemy/>`__             |
+---------------------+----------------------------------------------------------------------------------------------+
| Google App Engine   | `graphene-gae <https://github.com/graphql-python/graphene-gae/>`__                           |
+---------------------+----------------------------------------------------------------------------------------------+
| Peewee              | *In progress* (`Tracking Issue <https://github.com/graphql-python/graphene/issues/289>`__)   |
+---------------------+----------------------------------------------------------------------------------------------+

Also, Graphene is fully compatible with the GraphQL spec, working
seamlessly with all GraphQL clients, such as
`Relay <https://github.com/facebook/relay>`__,
`Apollo <https://github.com/apollographql/apollo-client>`__ and
`gql <https://github.com/graphql-python/gql>`__.

Installation
------------

For instaling graphene, just run this command in your shell

.. code:: bash

    pip install "graphene>=1.0"

1.0 Upgrade Guide
-----------------

Please read `UPGRADE-v1.0.md </UPGRADE-v1.0.md>`__ to learn how to
upgrade.

Examples
--------

Here is one example for you to get started:

.. code:: python

    class Query(graphene.ObjectType):
        hello = graphene.String(description='A typical hello world')

        def resolve_hello(self, args, context, info):
            return 'World'

    schema = graphene.Schema(query=Query)

Then Querying ``graphene.Schema`` is as simple as:

.. code:: python

    query = '''
        query SayHello {
          hello
        }
    '''
    result = schema.execute(query)

If you want to learn even more, you can also check the following
`examples <examples/>`__:

-  **Basic Schema**: `Starwars example <examples/starwars>`__
-  **Relay Schema**: `Starwars Relay
   example <examples/starwars_relay>`__

Contributing
------------

After cloning this repo, ensure dependencies are installed by running:

.. code:: sh

    pip install -e ".[test]"

After developing, the full test suite can be evaluated by running:

.. code:: sh

    py.test graphene --cov=graphene --benchmark-skip # Use -v -s for verbose mode

You can also run the benchmarks with:

.. code:: sh

    py.test graphene --benchmark-only

Documentation
~~~~~~~~~~~~~

The documentation is generated using the excellent
`Sphinx <http://www.sphinx-doc.org/>`__ and a custom theme.

The documentation dependencies are installed by running:

.. code:: sh

    cd docs
    pip install -r requirements.txt

Then to produce a HTML version of the documentation:

.. code:: sh

    make html

.. |Graphene Logo| image:: http://graphene-python.org/favicon.png
.. |Build Status| image:: https://travis-ci.org/graphql-python/graphene.svg?branch=master
   :target: https://travis-ci.org/graphql-python/graphene
.. |PyPI version| image:: https://badge.fury.io/py/graphene.svg
   :target: https://badge.fury.io/py/graphene
.. |Coverage Status| image:: https://coveralls.io/repos/graphql-python/graphene/badge.svg?branch=master&service=github
   :target: https://coveralls.io/github/graphql-python/graphene?branch=master
