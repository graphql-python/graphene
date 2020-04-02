API Reference
=============

Schema
------

.. autoclass:: graphene.types.schema.Schema
    :members:

.. Uncomment sections / types as API documentation is fleshed out
.. in each class

Object types
------------

.. autoclass:: graphene.ObjectType

.. autoclass:: graphene.InputObjectType

.. autoclass:: graphene.Mutation
    :members:

.. _fields-mounted-types:

Fields (Mounted Types)
----------------------

.. autoclass:: graphene.Field

.. autoclass:: graphene.Argument

.. autoclass:: graphene.InputField

Fields (Unmounted Types)
------------------------

.. autoclass:: graphene.types.unmountedtype.UnmountedType

GraphQL Scalars
---------------

.. autoclass:: graphene.Int()

.. autoclass:: graphene.Float()

.. autoclass:: graphene.String()

.. autoclass:: graphene.Boolean()

.. autoclass:: graphene.ID()

Graphene Scalars
----------------

.. autoclass:: graphene.Date()

.. autoclass:: graphene.DateTime()

.. autoclass:: graphene.Time()

.. autoclass:: graphene.Decimal()

.. autoclass:: graphene.UUID()

.. autoclass:: graphene.JSONString()

Enum
----

.. autoclass:: graphene.Enum()

Structures
----------

.. autoclass:: graphene.List

.. autoclass:: graphene.NonNull

Type Extension
--------------

.. autoclass:: graphene.Interface()

.. autoclass:: graphene.Union()

Execution Metadata
------------------

.. autoclass:: graphene.ResolveInfo

.. autoclass:: graphene.Context

.. autoclass:: graphql.execution.base.ExecutionResult

.. Relay
.. -----

.. .. autoclass:: graphene.Node

.. .. autoclass:: graphene.GlobalID

.. .. autoclass:: graphene.ClientIDMutation

.. .. autoclass:: graphene.Connection

.. .. autoclass:: graphene.ConnectionField

.. .. autoclass:: graphene.PageInfo
