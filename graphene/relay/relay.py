import collections

from graphene import signals
from graphene.utils import cached_property

from graphql_relay.node.node import (
    globalIdField
)
from graphql_relay.connection.arrayconnection import (
    connectionFromArray
)
from graphql_relay.connection.connection import (
    connectionArgs,
    connectionDefinitions
)
from graphene.relay.nodes import create_node_definitions
from graphene.core.fields import Field, NativeField

Node, NodeField = create_node_definitions()

class ConnectionField(Field):
    def __init__(self, field_type, resolve=None, description=''):
        super(ConnectionField, self).__init__(field_type, resolve=resolve, 
                                              args=connectionArgs, description=description)

    def resolve(self, instance, args, info):
        resolved = super(ConnectionField, self).resolve(instance, args, info)
        if resolved:
            assert isinstance(resolved, collections.Iterable), 'Resolved value from the connection field have to be iterable'
            return connectionFromArray(resolved, args)

    @cached_property
    def type(self):
        object_type = self.get_object_type()
        assert issubclass(object_type, Node), 'Only nodes have connections.'
        return object_type.connection


@signals.class_prepared.connect
def object_type_created(object_type):
    if issubclass(object_type, Node):
        type_name = object_type._meta.type_name
        # def getId(*args, **kwargs):
        #     print '**GET ID', args, kwargs
        #     return 2
        field = NativeField(globalIdField(type_name))
        object_type.add_to_class('id', field)
        assert hasattr(object_type, 'get_node'), 'get_node classmethod not found in %s Node' % type_name

        connection = connectionDefinitions(type_name, object_type._meta.type).connectionType
        object_type.add_to_class('connection', connection)
