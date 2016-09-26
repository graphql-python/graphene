Please read `UPGRADE-v1.0.md`_ to learn how to upgrade to Graphene ``1.0``.

--------------

|Graphene Logo| `Graphene`_ |Build Status| |PyPI version| |Coverage Status|
===========================================================================

`Graphene`_ is a Python library for building GraphQL schemas/types fast
and easily.

-  **Easy to use:** Graphene helps you use GraphQL in Python without
   effort.
-  **Relay:** Graphene has builtin support for Relay
-  **Data agnostic:** Graphene supports any kind of data source: SQL
   (Django, SQLAlchemy), NoSQL, custom Python objects, etc. We believe that
   by providing a complete API you could plug Graphene anywhere your
   data lives and make your data available through GraphQL.

Integrations
------------

Graphene has multiple integrations with different frameworks:

+---------------------+-------------------------------------+
| integration         | Package                             |
+=====================+=====================================+
| Django              | `graphene-django`_                  |
+---------------------+-------------------------------------+
| SQLAlchemy          | `graphene-sqlalchemy`_              |
+---------------------+-------------------------------------+
| Google App Engine   | `graphene-gae`_                     |
+---------------------+-------------------------------------+
| Peewee              | *In progress* (`Tracking Issue`_)   |
+---------------------+-------------------------------------+

Installation
------------

For instaling graphene, just run this command in your shell

.. code:: bash

    pip install "graphene>=1.0"

1.0 Upgrade Guide
-----------------

Please read `UPGRADE-v1.0.md`_ to learn how to upgrade.

Examples
--------

Here is one example for get you started:

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
`examples`_:

-  **Basic Schema**: `Starwars example`_
-  **Relay Schema**: `Starwars Relay example`_

Contributing
------------

After cloning this repo, ensure dependencies are installed by running:

.. code:: sh

    python setup.py install

After developing, the full test suite can be evaluated by running:

.. code:: sh

    python setup.py test # Use --pytest-args="-v -s" for verbose mode

.. _UPGRADE-v1.0.md: /UPGRADE-v1.0.md
.. _Graphene: http://graphene-python.org
.. _graphene-django: https://github.com/graphql-python/graphene-django/
.. _graphene-sqlalchemy: https://github.com/graphql-python/graphene-sqlalchemy/
.. _graphene-gae: https://github.com/graphql-python/graphene-gae/
.. _Tracking Issue: https://github.com/graphql-python/graphene/issues/289
.. _examples: examples/
.. _Starwars example: examples/starwars
.. _Starwars Relay example: examples/starwars_relay

.. |Graphene Logo| image:: http://graphene-python.org/favicon.png
.. |Build Status| image:: https://travis-ci.org/graphql-python/graphene.svg?branch=master
   :target: https://travis-ci.org/graphql-python/graphene
.. |PyPI version| image:: https://badge.fury.io/py/graphene.svg
   :target: https://badge.fury.io/py/graphene
.. |Coverage Status| image:: https://coveralls.io/repos/graphql-python/graphene/badge.svg?branch=master&service=github
   :target: https://coveralls.io/github/graphql-python/graphene?branch=master
