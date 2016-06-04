from functools import partial
import six
from graphql_relay import node_definitions, from_global_id

from ..types.definitions import GrapheneInterfaceType
from ..types.field import Field
from ..types.interface import Interface, InterfaceTypeMeta


class NodeMeta(InterfaceTypeMeta):

    def construct_graphql_type(cls, bases):
        pass

    def construct(cls, *args, **kwargs):
        constructed = super(NodeMeta, cls).construct(*args, **kwargs)
        if not cls._meta.graphql_type:
            node_interface, node_field = node_definitions(
                cls.get_node,
                interface_class=partial(GrapheneInterfaceType, graphene_type=cls),
                field_class=Field
            )
            cls._meta.graphql_type = node_interface
            cls.Field = node_field
        return constructed


class Node(six.with_metaclass(NodeMeta, Interface)):

    @classmethod
    def require_get_node(cls):
        return cls == Node

    @classmethod
    def from_global_id(cls, global_id):
        return from_global_id(global_id)

    @classmethod
    def get_node(cls, global_id, context, info):
        try:
            _type, _id = cls.from_global_id(global_id)
        except:
            return None
        graphql_type = info.schema.get_type(_type)
        if cls._meta.graphql_type not in graphql_type.get_interfaces():
            return
        return graphql_type.graphene_type.get_node(_id, context, info)

    @classmethod
    def implements(cls, object_type):
        '''
        We check here that the object_type have the required get_node method
        in it
        '''
        if cls.require_get_node():
            assert hasattr(object_type, 'get_node'), '{}.get_node method is required by the Node interface.'.format(object_type._meta.graphql_type.name)
        return super(Node, cls).implements(object_type)
