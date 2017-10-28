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

It's possible to add a description to an enum value, for that the enum value
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

In case the Enums are already defined it's possible to reuse them using
the ``Enum.from_enum`` function.

.. code:: python

    graphene.Enum.from_enum(AlreadyExistingPyEnum)


Notes
-----

``graphene.Enum`` uses |enum.Enum|_ internally (or a backport if
that's not available) and can be used in a similar way, with the exception of
member getters.

In the Python ``Enum`` implementation you can access a member by initing the Enum.

.. code:: python
    
    from enum import Enum
    class Color(Enum):
        RED = 1
        GREEN = 2
        BLUE = 3

    assert Color(1) == Color.RED


However, in Graphene ``Enum`` you need to call get to have the same effect:

.. code:: python
    
    from graphene import Enum
    class Color(Enum):
        RED = 1
        GREEN = 2
        BLUE = 3

    assert Color.get(1) == Color.RED

.. |enum.Enum| replace:: ``enum.Enum``
.. _enum.Enum: https://docs.python.org/3/library/enum.html
