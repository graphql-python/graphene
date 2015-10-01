from graphql_relay.node.node import (
    globalIdField
)

from graphene import signals
from graphene.relay.fields import NodeIDField
from graphene.relay.types import BaseNode, Node

@signals.class_prepared.connect
def object_type_created(object_type):
    if issubclass(object_type, BaseNode) and BaseNode not in object_type.__bases__:
        type_name = object_type._meta.type_name
        field = NodeIDField()
        object_type.add_to_class('id', field)
        assert hasattr(object_type, 'get_node'), 'get_node classmethod not found in %s Node' % type_name
