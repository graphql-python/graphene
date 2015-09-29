from graphql_relay.node.node import (
    nodeDefinitions,
    fromGlobalId
)
from graphene.env import get_global_schema
from graphene.core.types import Interface
from graphene.core.fields import LazyNativeField


def get_node_type(obj):
    return obj._meta.type


def get_node(schema, globalId, *args):
    resolvedGlobalId = fromGlobalId(globalId)
    _type, _id = resolvedGlobalId.type, resolvedGlobalId.id
    object_type = schema.get_type(_type)
    return object_type.get_node(_id)

class Node(Interface):
    _definitions = None

    @classmethod
    def contribute_to_schema(cls, schema):
        if cls._definitions:
            return
        schema = cls._meta.schema
        cls._definitions = nodeDefinitions(lambda *args: get_node(schema, *args), get_node_type)

    @classmethod
    def get_graphql_type(cls):
        if cls is cls._meta.schema.Node:
            # Return only nodeInterface when is the Node Inerface
            cls.contribute_to_schema(cls._meta.schema)
            return cls._definitions.nodeInterface
        return super(Node, cls).get_graphql_type()

