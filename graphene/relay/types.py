from graphql_relay.node.node import (
    to_global_id
)
from graphql_relay.connection.connection import (
    connection_definitions
)

from graphene.core.types import Interface
from graphene.relay.fields import GlobalIDField
from graphene.utils import memoize


class BaseNode(object):
    @classmethod
    @memoize
    def get_connection(cls, schema):
        _type = cls.internal_type(schema)
        type_name = cls._meta.type_name
        connection = connection_definitions(type_name, _type).connection_type
        return connection

    @classmethod
    def _prepare_class(cls):
        from graphene.relay.utils import is_node
        if is_node(cls):
            assert hasattr(
                cls, 'get_node'), 'get_node classmethod not found in %s Node' % cls

    @classmethod
    def to_global_id(cls, instance, args, info):
        type_name = cls._meta.type_name
        return to_global_id(type_name, instance.id)


class Node(BaseNode, Interface):
    '''An object with an ID'''
    id = GlobalIDField()
