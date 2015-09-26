from graphql_relay.node.node import (
    nodeDefinitions,
    fromGlobalId
)

def create_node_definitions(getNode=None, getNodeType=None, schema=None):
    from graphene.core.types import Interface
    from graphene.core.fields import Field, NativeField
    if not getNode:
        def getNode(globalId, *args):
            from graphene.env import get_global_schema
            _schema = schema or get_global_schema()
            resolvedGlobalId = fromGlobalId(globalId)
            _type, _id = resolvedGlobalId.type, resolvedGlobalId.id
            object_type = _schema.get_type(_type) 
            return object_type.get_node(_id)

    if not getNodeType:
        def getNodeType(obj):
            return obj._meta.type

    _nodeDefinitions = nodeDefinitions(getNode, getNodeType)


    class Node(Interface):
        @classmethod
        def get_graphql_type(cls):
            if cls is Node:
                # Return only nodeInterface when is the Node Inerface
                return _nodeDefinitions.nodeInterface
            return super(Node, cls).get_graphql_type()


    class NodeField(NativeField):
        field = _nodeDefinitions.nodeField

    return Node, NodeField
