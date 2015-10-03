from graphql_relay.node.node import (
    globalIdField
)

from graphene import signals
from graphene.relay.fields import NodeIDField
from graphene.relay.utils import is_node


@signals.class_prepared.connect
def object_type_created(object_type):
    if is_node(object_type):
        type_name = object_type._meta.type_name
        field = NodeIDField()
        object_type.add_to_class('id', field)
        assert hasattr(
            object_type, 'get_node'), 'get_node classmethod not found in %s Node' % type_name
