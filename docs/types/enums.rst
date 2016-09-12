Enums
=====

A ``Enum`` is a special ``GraphQL`` type that represents a set of
symbolic names (members) bound to unique, constant values.

Definition
----------

You can create an ``Enum`` using classes:

.. code:: python

    import graphene

    class Episode(graphene.Enum):
        NEWHOPE = 4
        EMPIRE = 5
        JEDI = 6

But also using instances of Enum:

.. code:: python

    Episode = graphene.Enum('Episode', [('NEWHOPE', 4), ('EMPIRE', 5), ('JEDI', 6)])

Value descriptions
------------------

It's possible to add a description to a enum value, for that the the enum value
needs to have the ``description`` property on it.

.. code:: python

    class Episode(graphene.Enum):
        NEWHOPE = 4
        EMPIRE = 5
        JEDI = 6

        @property
        def description(self):
            if self == Episode.NEWHOPE:
                return 'New Hope Episode'
            return 'Other episode'


Usage with Python Enums
-----------------------

In case that the Enums are already defined it's possible to reuse them using
the ``Enum.from_enum`` function.

.. code:: python

    graphene.Enum.from_enum(AlreadyExistingPyEnum)


Notes
-----

Internally, ``graphene.Enum`` uses `enum.Enum`_ Python
implementation if available, or a backport if not.

So you can use it in the same way as you would do with Python
``enum.Enum``.

.. _``enum.Enum``: https://docs.python.org/3/library/enum.html
