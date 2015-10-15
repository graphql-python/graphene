from graphql_relay.node.node import (
    node_definitions,
    from_global_id
)
from graphql_relay.connection.connection import (
    connection_definitions
)

from graphene.core.types import Interface
from graphene.core.fields import LazyNativeField
from graphene.utils import memoize


def get_node_type(schema, obj, info=None):
    return obj.internal_type(schema)


def get_node(schema, global_id, *args):
    resolved_global_id = from_global_id(global_id)
    _type, _id = resolved_global_id.type, resolved_global_id.id
    object_type = schema.get_type(_type)
    if not object_type or not issubclass(object_type, BaseNode):
        raise Exception("The type %s is not a Node" % _type)
    return object_type.get_node(_id)


class BaseNode(object):

    @classmethod
    @memoize
    def get_definitions(cls, schema):
        return node_definitions(lambda *args: get_node(schema, *args), lambda *args: get_node_type(schema, *args))

    @classmethod
    @memoize
    def get_connection(cls, schema):
        _type = cls.internal_type(schema)
        type_name = cls._meta.type_name
        connection = connection_definitions(type_name, _type).connection_type
        return connection

    @classmethod
    def internal_type(cls, schema):
        from graphene.relay.utils import is_node_type
        if is_node_type(cls):
            # Return only node_interface when is the Node Inerface
            return BaseNode.get_definitions(schema).node_interface
        return super(BaseNode, cls).internal_type(schema)


class Node(BaseNode, Interface):
    pass
