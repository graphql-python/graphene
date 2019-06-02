Connection
==========

A connection is a vitaminized version of a List that provides ways of
slicing and paginating through it. The way you create Connection types
in ``graphene`` is using ``relay.Connection`` and ``relay.ConnectionField``.

Quick example
-------------

If we want to create a custom Connection on a given node, we have to subclass the
``Connection`` class.

In the following example, ``extra`` will be an extra field in the connection,
and ``other`` an extra field in the Connection Edge.

.. code:: python

    class ShipConnection(Connection, node=Ship):
        extra = String()

        class Edge:
            other = String()

The ``ShipConnection`` connection class, will have automatically a ``pageInfo`` field,
and a ``edges`` field (which is a list of ``ShipConnection.Edge``).
This ``Edge`` will have a ``node`` field linking to the specified node
(in ``ShipConnection.Meta``) and the field ``other`` that we defined in the class.

Connection Field
----------------
You can create connection fields in any Connection, in case any ObjectType
that implements ``Node`` will have a default Connection.

.. code:: python

    class Faction(ObjectType):
        name = String()
        ships = relay.ConnectionField(ShipConnection)

        def resolve_ships(self, info):
            return []
