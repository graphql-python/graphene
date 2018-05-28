===================
Testing in Graphene
===================


Automated testing is an extremely useful bug-killing tool for the modern developer. You can use a collection of tests – a test suite – to solve, or avoid, a number of problems:

- When you’re writing new code, you can use tests to validate your code works as expected.
- When you’re refactoring or modifying old code, you can use tests to ensure your changes haven’t affected your application’s behavior unexpectedly.

Testing a GraphQL application is a complex task, because a GraphQL application is made of several layers of logic – schema definition, schema validation, permissions and field resolution.

With Graphene test-execution framework and assorted utilities, you can simulate GraphQL requests, execute mutations, inspect your application’s output and generally verify your code is doing what it should be doing.


Testing tools
-------------

Graphene provides a small set of tools that come in handy when writing tests.


Test Client
~~~~~~~~~~~

The test client is a Python class that acts as a dummy GraphQL client, allowing you to test your views and interact with your Graphene-powered application programmatically.

Some of the things you can do with the test client are:

- Simulate Queries and Mutations and observe the response.
- Test that a given query request is rendered by a given Django template, with a template context that contains certain values.


Overview and a quick example
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To use the test client, instantiate ``graphene.test.Client`` and retrieve GraphQL responses:


.. code:: python

    from graphene.test import Client

    def test_hey():
        client = Client(my_schema)
        executed = client.execute('''{ hey }''')
        assert executed == {
            'data': {
                'hey': 'hello!'
            }
        }


Execute parameters
~~~~~~~~~~~~~~~~~~

You can also add extra keyword arguments to the ``execute`` method, such as
``context_value``, ``root_value``, ``variable_values``, ...:


.. code:: python

    from graphene.test import Client

    def test_hey():
        client = Client(my_schema)
        executed = client.execute('''{ hey }''', context_value={'user': 'Peter'})
        assert executed == {
            'data': {
                'hey': 'hello Peter!'
            }
        }


Snapshot testing
~~~~~~~~~~~~~~~~

As our APIs evolve, we need to know when our changes introduce any breaking changes that might break
some of the clients of our GraphQL app.

However, writing tests and replicate the same response we expect from our GraphQL application can be
tedious and repetitive task, and sometimes it's easier to skip this process.

Because of that, we recommend the usage of `SnapshotTest <https://github.com/syrusakbary/snapshottest/>`_.

SnapshotTest let us write all this tests in a breeze, as creates automatically the ``snapshots`` for us
the first time the test is executed.


Here is a simple example on how our tests will look if we use ``pytest``:

.. code:: python

    def test_hey(snapshot):
        client = Client(my_schema)
        # This will create a snapshot dir and a snapshot file
        # the first time the test is executed, with the response
        # of the execution.
        snapshot.assert_match(client.execute('''{ hey }'''))


If we are using ``unittest``:

.. code:: python

    from snapshottest import TestCase

    class APITestCase(TestCase):
        def test_api_me(self):
            """Testing the API for /me"""
            client = Client(my_schema)
            self.assertMatchSnapshot(client.execute('''{ hey }'''))
