from graphql_relay.node.node import (
    nodeDefinitions,
    fromGlobalId
)
from graphql_relay.connection.connection import (
    connectionDefinitions
)

from graphene.env import get_global_schema
from graphene.core.types import Interface
from graphene.core.fields import LazyNativeField
from graphene.utils import memoize


def get_node_type(schema, obj):
    return obj.internal_type(schema)


def get_node(schema, globalId, *args):
    resolvedGlobalId = fromGlobalId(globalId)
    _type, _id = resolvedGlobalId.type, resolvedGlobalId.id
    object_type = schema.get_type(_type)
    return object_type.get_node(_id)


class BaseNode(object):
    @classmethod
    @memoize
    def get_definitions(cls, schema):
        return nodeDefinitions(lambda *args: get_node(schema, *args), lambda *args: get_node_type(schema, *args))

    @classmethod
    @memoize
    def get_connection(cls, schema):
        _type = cls.internal_type(schema)
        type_name = cls._meta.type_name
        connection = connectionDefinitions(type_name, _type).connectionType
        return connection

    @classmethod
    def internal_type(cls, schema):
        if cls is Node or BaseNode in cls.__bases__:
            # Return only nodeInterface when is the Node Inerface
            return BaseNode.get_definitions(schema).nodeInterface
        return super(BaseNode, cls).internal_type(schema)


class Node(BaseNode, Interface):
    pass
