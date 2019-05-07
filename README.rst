**We are looking for contributors**! Please check the
`ROADMAP <https://github.com/graphql-python/graphene/blob/master/ROADMAP.md>`__
to see how you can help ❤️

--------------

|Graphene Logo| `Graphene <http://graphene-python.org>`__ |Build Status| |PyPI version| |Coverage Status|
=========================================================================================================

.. raw:: html

   <h1 align="center">

Supporting Graphene Python

.. raw:: html

   </h1>

Graphene is an MIT-licensed open source project. It's an independent
project with its ongoing development made possible entirely thanks to
the support by these awesome
`backers <https://github.com/graphql-python/graphene/blob/master/BACKERS.md>`__.
If you'd like to join them, please consider:

-  `Become a backer or sponsor on
   Patreon <https://www.patreon.com/syrusakbary>`__.
-  `One-time donation via
   PayPal. <https://graphene-python.org/support-graphene/>`__

<!--

.. raw:: html

   <h2 align="center">

Special Sponsors

.. raw:: html

   </h2>

.. raw:: html

   <p align="center">

.. raw:: html

   </p>

.. raw:: html

   <!--special end-->

.. raw:: html

   <h2 align="center">

Platinum via Patreon

.. raw:: html

   </h2>

.. raw:: html

   <!--platinum start-->

.. raw:: html

   <table>

.. raw:: html

   <tbody>

::

    <tr>
      <td align="center" valign="middle">
        <a href="https://www.patreon.com/join/syrusakbary" target="_blank">
          <img width="222px" src="https://raw.githubusercontent.com/graphql-python/graphene-python.org/master/src/pages/sponsors/generic-logo.png">
        </a>
      </td>
    </tr>

.. raw:: html

   </tbody>

.. raw:: html

   </table>

.. raw:: html

   <h2 align="center">

Gold via Patreon

.. raw:: html

   </h2>

.. raw:: html

   <!--gold start-->

.. raw:: html

   <table>

.. raw:: html

   <tbody>

::

    <tr>
      <td align="center" valign="middle">
        <a href="https://www.patreon.com/join/syrusakbary" target="_blank">
          <img width="148px" src="https://raw.githubusercontent.com/graphql-python/graphene-python.org/master/src/pages/sponsors/generic-logo.png">
        </a>
      </td>
    </tr>

.. raw:: html

   </tbody>

.. raw:: html

   </table>

.. raw:: html

   <!--gold end-->

.. raw:: html

   <h2 align="center">

Silver via Patreon

.. raw:: html

   </h2>

.. raw:: html

   <!--silver start-->

.. raw:: html

   <table>

.. raw:: html

   <tbody>

::

    <tr>
      <td align="center" valign="middle">
        <a href="https://www.patreon.com/join/syrusakbary" target="_blank">
          <img width="148px" src="https://raw.githubusercontent.com/graphql-python/graphene-python.org/master/src/pages/sponsors/generic-logo.png">
        </a>
      </td>
    </tr>

.. raw:: html

   </tbody>

.. raw:: html

   </table>

.. raw:: html

   <!--silver end-->

--------------

Introduction
------------

`Graphene <http://graphene-python.org>`__ is a Python library for
building GraphQL schemas/types fast and easily.

-  **Easy to use:** Graphene helps you use GraphQL in Python without
   effort.
-  **Relay:** Graphene has builtin support for Relay.
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

    pip install "graphene>=2.0"

2.0 Upgrade Guide
-----------------

Please read `UPGRADE-v2.0.md </UPGRADE-v2.0.md>`__ to learn how to
upgrade.

Examples
--------

Here is one example for you to get started:

.. code:: python

    class Query(graphene.ObjectType):
        hello = graphene.String(description='A typical hello world')

        def resolve_hello(self, info):
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

Documentation
-------------

Documentation and links to additional resources are available at
https://docs.graphene-python.org/en/latest/

Contributing
------------

See `Contributing <CONTRIBUTING.md>`__

.. |Graphene Logo| image:: http://graphene-python.org/favicon.png
.. |Build Status| image:: https://travis-ci.org/graphql-python/graphene.svg?branch=master
   :target: https://travis-ci.org/graphql-python/graphene
.. |PyPI version| image:: https://badge.fury.io/py/graphene.svg
   :target: https://badge.fury.io/py/graphene
.. |Coverage Status| image:: https://coveralls.io/repos/graphql-python/graphene/badge.svg?branch=master&service=github
   :target: https://coveralls.io/github/graphql-python/graphene?branch=master
