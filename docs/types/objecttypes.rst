.. _ObjectType:

ObjectType
==========

A Graphene *ObjectType* is the building block used to define the relationship between **Fields** in your **Schema** and how their data is retrieved.

The basics:

- Each ObjectType is a Python class that inherits from ``graphene.ObjectType``.
- Each attribute of the ObjectType represents a ``Field``.
- Each ``Field`` has a :ref:`resolver method<Resolvers>` to fetch data (or :ref:`DefaultResolver`).

Quick example
-------------

This example model defines a Person, with a first and a last name:

.. code:: python

    from graphene import ObjectType, String

    class Person(ObjectType):
        first_name = String()
        last_name = String()
        full_name = String()

        def resolve_full_name(parent, info):
            return f"{parent.first_name} {parent.last_name}"

This *ObjectType* defines the field **first\_name**, **last\_name**, and **full\_name**. Each field is specified as a class attribute, and each attribute maps to a Field. Data is fetched by our ``resolve_full_name`` :ref:`resolver method<Resolvers>` for ``full_name`` field and the :ref:`DefaultResolver` for other fields.

The above ``Person`` ObjectType has the following schema representation:

.. code::

    type Person {
      firstName: String
      lastName: String
      fullName: String
    }

.. _Resolvers:

Resolvers
---------

A **Resolver** is a method that helps us answer **Queries** by fetching data for a **Field** in our **Schema**.

Resolvers are lazily executed, so if a field is not included in a query, its resolver will not be executed.

Each field on an *ObjectType* in Graphene should have a corresponding resolver method to fetch data. This resolver method should match the field name. For example, in the ``Person`` type above, the ``full_name`` field is resolved by the method ``resolve_full_name``.

Each resolver method takes the parameters:
* :ref:`ResolverParamParent` for the value object use to resolve most fields
* :ref:`ResolverParamInfo` for query and schema meta information and per-request context
* :ref:`ResolverParamGraphQLArguments` as defined on the **Field**.

.. _ResolverArguments:

Resolver Parameters
~~~~~~~~~~~~~~~~~~~

.. _ResolverParamParent:

Parent Value Object (*parent*)
******************************

This parameter is typically used to derive the values for most fields on an *ObjectType*.

The first parameter of a resolver method (*parent*) is the value object returned from the resolver of the parent field. If there is no parent field, such as a root Query field, then the value for *parent* is set to the ``root_value`` configured while executing the query (default ``None``). See :ref:`SchemaExecute` for more details on executing queries.

Resolver example
^^^^^^^^^^^^^^^^

If we have a schema with Person type and one field on the root query.

.. code:: python

    from graphene import ObjectType, String, Field

    class Person(ObjectType):
        full_name = String()

        def resolve_full_name(parent, info):
            return f"{parent.first_name} {parent.last_name}"

    class Query(ObjectType):
        me = Field(Person)

        def resolve_me(parent, info):
            # returns an object that represents a Person
            return get_human(name="Luke Skywalker")

When we execute a query against that schema.

.. code:: python

    schema = Schema(query=Query)

    query_string = "{ me { fullName } }"
    result = schema.execute(query_string)

    assert result.data["me"] == {"fullName": "Luke Skywalker")

Then we go through the following steps to resolve this query:

* ``parent`` is set with the root_value from query execution (None).
* ``Query.resolve_me`` called with ``parent`` None which returns a value object ``Person("Luke", "Skywalker")``.
* This value object is then used as ``parent`` while calling ``Person.resolve_full_name`` to resolve the scalar String value "Luke Skywalker".
* The scalar value is serialized and sent back in the query response.

Each resolver returns the next :ref:`ResolverParamParent` to be used in executing the following resolver in the chain. If the Field is a Scalar type, that value will be serialized and sent in the **Response**. Otherwise, while resolving Compound types like *ObjectType*, the value be passed forward as the next :ref:`ResolverParamParent`.

Naming convention
^^^^^^^^^^^^^^^^^

This :ref:`ResolverParamParent` is sometimes named ``obj``, ``parent``, or ``source`` in other GraphQL documentation. It can also be named after the value object being resolved (ex. ``root`` for a root Query or Mutation, and ``person`` for a Person value object). Sometimes this argument will be named ``self`` in Graphene code, but this can be misleading due to :ref:`ResolverImplicitStaticMethod` while executing queries in Graphene.

.. _ResolverParamInfo:

GraphQL Execution Info (*info*)
*******************************

The second parameter provides two things:

* reference to meta information about the execution of the current GraphQL Query (fields, schema, parsed query, etc.)
* access to per-request ``context`` which can be used to store user authentication, data loader instances or anything else useful for resolving the query.

Only context will be required for most applications. See :ref:`SchemaExecuteContext` for more information about setting context.

.. _ResolverParamGraphQLArguments:

GraphQL Arguments (*\*\*kwargs*)
********************************

Any arguments that a field defines gets passed to the resolver function as
keyword arguments. For example:

.. code:: python

    from graphene import ObjectType, Field, String

    class Query(ObjectType):
        human_by_name = Field(Human, name=String(required=True))

        def resolve_human_by_name(parent, info, name):
            return get_human(name=name)

You can then execute the following query:

.. code::

    query {
        humanByName(name: "Luke Skywalker") {
            firstName
            lastName
        }
    }

Convenience Features of Graphene Resolvers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. _ResolverImplicitStaticMethod:

Implicit staticmethod
*********************

One surprising feature of Graphene is that all resolver methods are treated implicitly as staticmethods. This means that, unlike other methods in Python, the first argument of a resolver is *never* ``self`` while it is being executed by Graphene. Instead, the first argument is always :ref:`ResolverParamParent`.  In practice, this is very convenient as, in GraphQL, we are almost always more concerned with the using the parent value object to resolve queries than attributes on the Python object itself.

The two resolvers in this example are effectively the same.

.. code:: python

    from graphene import ObjectType, String

    class Person(ObjectType):
        first_name = String()
        last_name = String()

        @staticmethod
        def resolve_first_name(parent, info):
            '''
            Decorating a Python method with `staticmethod` ensures that `self` will not be provided as an
            argument. However, Graphene does not need this decorator for this behavior.
            '''
            return parent.first_name

        def resolve_last_name(parent, info):
            '''
            Normally the first argument for this method would be `self`, but Graphene executes this as
            a staticmethod implicitly.
            '''
            return parent.last_name

        # ...

If you prefer your code to be more explicit, feel free to use ``@staticmethod`` decorators. Otherwise, your code may be cleaner without them!

.. _DefaultResolver:

Default Resolver
****************

If a resolver method is not defined for a **Field** attribute on our *ObjectType*, Graphene supplies a default resolver.

If the :ref:`ResolverParamParent` is a dictionary, the resolver will look for a dictionary key matching the field name. Otherwise, the resolver will get the attribute from the parent value object matching the field name.

.. code:: python

    from collections import namedtuple

    from graphene import ObjectType, String, Field, Schema

    PersonValueObject = namedtuple("Person", ["first_name", "last_name"])

    class Person(ObjectType):
        first_name = String()
        last_name = String()

    class Query(ObjectType):
        me = Field(Person)
        my_best_friend = Field(Person)

        def resolve_me(parent, info):
            # always pass an object for `me` field
            return PersonValueObject(first_name="Luke", last_name="Skywalker")

        def resolve_my_best_friend(parent, info):
            # always pass a dictionary for `my_best_fiend_field`
            return {"first_name": "R2", "last_name": "D2"}

    schema = Schema(query=Query)
    result = schema.execute('''
        {
            me { firstName lastName }
            myBestFriend { firstName lastName }
        }
    ''')
    # With default resolvers we can resolve attributes from an object..
    assert result.data["me"] == {"firstName": "Luke", "lastName": "Skywalker"}

    # With default resolvers, we can also resolve keys from a dictionary..
    assert result.data["myBestFriend"] == {"firstName": "R2", "lastName": "D2"}

Advanced
~~~~~~~~

GraphQL Argument defaults
*************************

If you define an argument for a field that is not required (and in a query
execution it is not provided as an argument) it will not be passed to the
resolver function at all. This is so that the developer can differentiate
between a ``undefined`` value for an argument and an explicit ``null`` value.

For example, given this schema:

.. code:: python

    from graphene import ObjectType, String

    class Query(ObjectType):
        hello = String(required=True, name=String())

        def resolve_hello(parent, info, name):
            return name if name else 'World'

And this query:

.. code::

    query {
        hello
    }

An error will be thrown:

.. code::

    TypeError: resolve_hello() missing 1 required positional argument: 'name'

You can fix this error in several ways. Either by combining all keyword arguments
into a dict:

.. code:: python

    from graphene import ObjectType, String

    class Query(ObjectType):
        hello = String(required=True, name=String())

        def resolve_hello(parent, info, **kwargs):
            name = kwargs.get('name', 'World')
            return f'Hello, {name}!'

Or by setting a default value for the keyword argument:

.. code:: python

    from graphene import ObjectType, String

    class Query(ObjectType):
        hello = String(required=True, name=String())

        def resolve_hello(parent, info, name='World'):
            return f'Hello, {name}!'

One can also set a default value for an Argument in the GraphQL schema itself using Graphene!

.. code:: python

    from graphene import ObjectType, String

    class Query(ObjectType):
        hello = String(
            required=True,
            name=String(default_value='World')
        )

        def resolve_hello(parent, info, name):
            return f'Hello, {name}!'

Resolvers outside the class
***************************

A field can use a custom resolver from outside the class:

.. code:: python

    from graphene import ObjectType, String

    def resolve_full_name(person, info):
        return '{} {}'.format(person.first_name, person.last_name)

    class Person(ObjectType):
        first_name = String()
        last_name = String()
        full_name = String(resolver=resolve_full_name)


Instances as value objects
**************************

Graphene ``ObjectType``\ s can act as value objects too. So with the
previous example you could use ``Person`` to capture data for each of the *ObjectType*'s fields.

.. code:: python

    peter = Person(first_name='Peter', last_name='Griffin')

    peter.first_name  # prints "Peter"
    peter.last_name  # prints "Griffin"

Field camelcasing
*****************

Graphene automatically camelcases fields on *ObjectType* from ``field_name`` to ``fieldName`` to conform with GraphQL standards. See :ref:`SchemaAutoCamelCase` for more information.

*ObjectType* Configuration - Meta class
---------------------------------------

Graphene uses a Meta inner class on *ObjectType* to set different options.

GraphQL type name
~~~~~~~~~~~~~~~~~

By default the type name in the GraphQL schema will be the same as the class name
that defines the ``ObjectType``. This can be changed by setting the ``name``
property on the ``Meta`` class:

.. code:: python

    from graphene import ObjectType

    class MyGraphQlSong(ObjectType):
        class Meta:
            name = 'Song'

GraphQL Description
~~~~~~~~~~~~~~~~~~~

The schema description of an *ObjectType* can be set as a docstring on the Python object or on the Meta inner class.

.. code:: python

    from graphene import ObjectType

    class MyGraphQlSong(ObjectType):
        ''' We can set the schema description for an Object Type here on a docstring '''
        class Meta:
            description = 'But if we set the description in Meta, this value is used instead'

Interfaces & Possible Types
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Setting ``interfaces`` in Meta inner class specifies the GraphQL Interfaces that this Object implements.

Providing ``possible_types`` helps Graphene resolve ambiguous types such as interfaces or Unions.

See :ref:`Interfaces` for more information.

.. code:: python

    from graphene import ObjectType, Node

    Song = namedtuple('Song', ('title', 'artist'))

    class MyGraphQlSong(ObjectType):
        class Meta:
            interfaces = (Node, )
            possible_types = (Song, )

.. _Interface: /docs/interfaces/
