Nodes
=====

A ``Node`` is an Interface provided by ``graphene.relay`` that contains
a single field ``id`` (which is a ``ID!``). Any object that inherits
from it have to implement a ``get_node`` method for retrieving a
``Node`` by an *id*.


Quick example
-------------

Example usage (taken from the `Starwars Relay example`_):

.. code:: python

    class Ship(graphene.ObjectType):
        '''A ship in the Star Wars saga'''
        class Meta:
            interfaces = (relay.Node, )

        name = graphene.String(description='The name of the ship.')

        @classmethod
        def get_node(cls, id, context, info):
            return get_ship(id)

The ``id`` returned by the ``Ship`` type when you query it will be a
scalar which contains the enough info for the server for knowing it’s
type and it’s id.

For example, the instance ``Ship(id=1)`` will return ``U2hpcDox`` as the
id when you query it (which is the base64 encoding of ``Ship:1``), and
which could be useful later if we want to query a node by its id.


Custom Nodes
------------

You can use the predefined ``relay.Node`` or you can subclass it, defining
custom ways of how a node id is encoded (using the ``to_global_id`` method in the class)
or how we can retrieve a Node given a encoded id (with the ``get_node_from_global_id`` method).

Example of a custom node:

.. code:: python

    class CustomNode(Node):

        class Meta:
            name = 'Node'

        @staticmethod
        def to_global_id(type, id):
            return '{}:{}'.format(type, id)

        @staticmethod
        def get_node_from_global_id(global_id, context, info):
            type, id = global_id.split(':')
            if type == 'User':
                return get_user(id)
            elif type == 'Photo':
                return get_photo(id)


The ``get_node_from_global_id`` method will be called when ``CustomNode.Field`` is resolved.


Node Root field
---------------

As is required in the `Relay specification`_, the server must implement
a root field called ``node`` that returns a ``Node`` Interface.

For this reason, ``graphene`` provides the field ``relay.Node.Field``,
which links to any type in the Schema which implements ``Node``.
Example usage:

.. code:: python

    class Query(graphene.ObjectType):
        # Should be CustomNode.Field() if we want to use our custom Node
        node = relay.Node.Field()

.. _Starwars Relay example: https://github.com/graphql-python/graphene/blob/master/examples/starwars_relay/schema.py
