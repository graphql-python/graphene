from graphql_relay.node.node import (
    nodeDefinitions,
    fromGlobalId
)
from graphene.env import get_global_schema
from graphene.core.types import Interface
from graphene.core.fields import Field, NativeField


def getSchemaNode(schema=None):
    def getNode(globalId, *args):
        _schema = schema or get_global_schema()
        resolvedGlobalId = fromGlobalId(globalId)
        _type, _id = resolvedGlobalId.type, resolvedGlobalId.id
        object_type = schema.get_type(_type) 
        return object_type.get_node(_id)
    return getNode


def getNodeType(obj):
    return obj._meta.type


def create_node_definitions(getNode=None, getNodeType=getNodeType, schema=None):
    getNode = getNode or getSchemaNode(schema)
    _nodeDefinitions = nodeDefinitions(getNode, getNodeType)

    _Interface = getattr(schema, 'Interface', Interface)

    class Node(_Interface):
        @classmethod
        def get_graphql_type(cls):
            if cls is Node:
                # Return only nodeInterface when is the Node Inerface
                return _nodeDefinitions.nodeInterface
            return super(Node, cls).get_graphql_type()


    class NodeField(NativeField):
        field = _nodeDefinitions.nodeField

    return Node, NodeField
