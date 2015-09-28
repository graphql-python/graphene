import collections

from graphql_relay.node.node import (
    globalIdField
)
from graphql_relay.connection.connection import (
    connectionDefinitions
)

from graphene import signals

from graphene.core.fields import NativeField
from graphene.relay.utils import get_relay
from graphene.relay.relay import Relay


@signals.class_prepared.connect
def object_type_created(object_type):
    relay = get_relay(object_type._meta.schema)
    if relay and issubclass(object_type, relay.Node):
        type_name = object_type._meta.type_name
        # def getId(*args, **kwargs):
        #     print '**GET ID', args, kwargs
        #     return 2
        field = NativeField(globalIdField(type_name))
        object_type.add_to_class('id', field)
        assert hasattr(object_type, 'get_node'), 'get_node classmethod not found in %s Node' % type_name

        connection = connectionDefinitions(type_name, object_type._meta.type).connectionType
        object_type.add_to_class('connection', connection)


@signals.init_schema.connect
def schema_created(schema):
    setattr(schema, 'relay', Relay(schema))
