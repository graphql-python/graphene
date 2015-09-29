from graphql_relay.node.node import (
    globalIdField
)
from graphql_relay.connection.connection import (
    connectionDefinitions
)

from graphene import signals
from graphene.core.fields import NativeField


@signals.class_prepared.connect
def object_type_created(object_type):
    schema = object_type._meta.schema
    if issubclass(object_type, schema.Node) and object_type != schema.Node:
        if object_type._meta.proxy:
            return
        type_name = object_type._meta.type_name
        field = NativeField(globalIdField(type_name))
        object_type.add_to_class('id', field)
        assert hasattr(object_type, 'get_node'), 'get_node classmethod not found in %s Node' % type_name

        connection = connectionDefinitions(type_name, object_type._meta.type).connectionType
        object_type.add_to_class('connection', connection)
