import collections

from graphene import signals
from graphene.core.fields import Field, NativeField
from graphene.core.types import Interface
from graphene.core.utils import get_type
from graphene.utils import cached_property

from graphql_relay.node.node import (
    nodeDefinitions,
    globalIdField,
    fromGlobalId
)
from graphql_relay.connection.arrayconnection import (
    connectionFromArray
)
from graphql_relay.connection.connection import (
    connectionArgs,
    connectionDefinitions
)

registered_nodes = {}


def getNode(globalId, *args):
    resolvedGlobalId = fromGlobalId(globalId)
    _type, _id = resolvedGlobalId.type, resolvedGlobalId.id
    if _type in registered_nodes:
        object_type = registered_nodes[_type]
        return object_type.get_node(_id)


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
        object_type = get_type(self.field_type, self.object_type)
        assert issubclass(object_type, Node), 'Only nodes have connections.'
        return object_type.connection


@signals.class_prepared.connect
def object_type_created(object_type):
    if issubclass(object_type, Node):
        type_name = object_type._meta.type_name
        assert type_name not in registered_nodes, 'Two nodes with the same type_name: %s' % type_name
        registered_nodes[type_name] = object_type
        # def getId(*args, **kwargs):
        #     print '**GET ID', args, kwargs
        #     return 2
        field = NativeField(globalIdField(type_name))
        object_type.add_to_class('id', field)
        assert hasattr(object_type, 'get_node'), 'get_node classmethod not found in %s Node' % type_name

        connection = connectionDefinitions(type_name, object_type._meta.type).connectionType
        object_type.add_to_class('connection', connection)
