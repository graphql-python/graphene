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

    class ShipConnection(Connection):
        extra = String()

        class Meta:
            node = Ship

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

The resolver of a connection field should return a list of objects of the
announced type. Those objects will automatically be wrapped in the edge and node
structure of the connection.

.. code:: python

    class Faction(graphene.ObjectType):
        name = graphene.String()
        ships = relay.ConnectionField(ShipConnection)

        def resolve_ships(self, info):
            # shall return a list of ship objects
            return get_ship_list()
