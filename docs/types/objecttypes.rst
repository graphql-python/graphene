ObjectTypes
===========

An ObjectType is the single, definitive source of information about your
data. It contains the essential fields and behaviors of the data you’re
querying.

The basics:

- Each ObjectType is a Python class that inherits from
  ``graphene.ObjectType``.
- Each attribute of the ObjectType represents a ``Field``.

Quick example
-------------

This example model defines a Person, with a first and a last name:

.. code:: python

    import graphene

    class Person(graphene.ObjectType):
        first_name = graphene.String()
        last_name = graphene.String()
        full_name = graphene.String()

        def resolve_full_name(root, info):
            return '{} {}'.format(root.first_name, root.last_name)

**first\_name** and **last\_name** are fields of the ObjectType. Each
field is specified as a class attribute, and each attribute maps to a
Field.

The above ``Person`` ObjectType has the following schema representation:

.. code::

    type Person {
      firstName: String
      lastName: String
      fullName: String
    }


Resolvers
---------

A resolver is a method that resolves certain fields within an
``ObjectType``. If not specified otherwise, the resolver of a
field is the ``resolve_{field_name}`` method on the ``ObjectType``.

By default resolvers take the arguments ``info`` and ``*args``.

NOTE: The resolvers on an ``ObjectType`` are always treated as ``staticmethod``\ s,
so the first argument to the resolver method ``self`` (or ``root``) need
not be an actual instance of the ``ObjectType``.

If an explicit resolver is not defined on the ``ObjectType`` then Graphene will
attempt to use a property with the same name on the object that is passed to the
``ObjectType``.

.. code:: python

    import graphene

    class Person(graphene.ObjectType):
        first_name = graphene.String()
        last_name = graphene.String()

    class Query(graphene.ObjectType):
        me = graphene.Field(Person)

        def resolve_me(_, info):
            # returns an object that represents a Person
            return get_human(name='Luke Skywalker')

If you are passing a dict instead of an object to your ``ObjectType`` you can
change the default resolver in the ``Meta`` class like this:

.. code:: python

    import graphene
    from graphene.types.resolver import dict_resolver

    class Person(graphene.ObjectType):
        class Meta:
            default_resolver = dict_resolver

        first_name = graphene.String()
        last_name = graphene.String()

    class Query(graphene.ObjectType):
        me = graphene.Field(Person)

        def resolve_me(_, info):
            return {
                "first_name": "Luke",
                "last_name": "Skywalker",
            }

Or you can change the default resolver globally by calling ``set_default_resolver``
before executing a query.

.. code:: python

    import graphene
    from graphene.types.resolver import dict_resolver, set_default_resolver

    set_default_resolver(dict_resolver)

    schema = graphene.Schema(query=Query)
    result = schema.execute('''
        query {
            me {
                firstName
            }
        }
     ''')


Resolvers with arguments
~~~~~~~~~~~~~~~~~~~~~~~~

Any arguments that a field defines gets passed to the resolver function as
kwargs. For example:

.. code:: python

    import graphene

    class Query(graphene.ObjectType):
        human_by_name = graphene.Field(Human, name=graphene.String(required=True))

        def resolve_human_by_name(_, info, name):
            return get_human(name=name)

You can then execute the following query:

.. code::

    query {
        humanByName(name: "Luke Skywalker") {
            firstName
            lastName
        }
    }

NOTE: if you define an argument for a field that is not required (and in a query
execution it is not provided as an argument) it will not be passed to the
resolver function at all. This is so that the developer can differenciate
between a ``undefined`` value for an argument and an explicit ``null`` value.

For example, given this schema:

.. code:: python

    import graphene

    class Query(graphene.ObjectType):
        hello = graphene.String(required=True, name=graphene.String())

        def resolve_hello(_, info, name):
            return name if name else 'World'

And this query:

.. code::

    query {
        hello
    }

An error will be thrown:

.. code::

    TypeError: resolve_hello() missing 1 required positional argument: 'name'

You can fix this error in 2 ways. Either by combining all keyword arguments
into a dict:

.. code:: python

    class Query(graphene.ObjectType):
        hello = graphene.String(required=True, name=graphene.String())

        def resolve_hello(_, info, **args):
            return args.get('name', 'World')

Or by setting a default value for the keyword argument:

.. code:: python

    class Query(graphene.ObjectType):
        hello = graphene.String(required=True, name=graphene.String())

        def resolve_hello(_, info, name='World'):
            return name


Resolvers outside the class
~~~~~~~~~~~~~~~~~~~~~~~~~~~

A field can use a custom resolver from outside the class:

.. code:: python

    import graphene

    def resolve_full_name(person, info):
        return '{} {}'.format(person.first_name, person.last_name)

    class Person(graphene.ObjectType):
        first_name = graphene.String()
        last_name = graphene.String()
        full_name = graphene.String(resolver=resolve_full_name)


Instances as data containers
----------------------------

Graphene ``ObjectType``\ s can act as containers too. So with the
previous example you could do:

.. code:: python

    peter = Person(first_name='Peter', last_name='Griffin')

    peter.first_name # prints "Peter"
    peter.last_name # prints "Griffin"

.. _Interface: /docs/interfaces/
