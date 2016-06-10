import copy
from functools import partial
import six
from graphql_relay import node_definitions, from_global_id, to_global_id

from ..types.field import Field
from ..types.objecttype import ObjectTypeMeta
from ..types.interface import GrapheneInterfaceType, Interface, InterfaceTypeMeta


class NodeMeta(ObjectTypeMeta):

    def construct(cls, bases, attrs):
        if not cls.is_object_type():
            cls.get_node = attrs.pop('get_node')
            cls.id_resolver = attrs.pop('id_resolver', None)
            node_interface, node_field = node_definitions(
                cls.get_node,
                id_resolver=cls.id_resolver,
                interface_class=partial(GrapheneInterfaceType, graphene_type=cls),
                field_class=Field,
            )
            cls._meta.graphql_type = node_interface
            cls.Field = partial(Field.copy_and_extend, node_field, type=None, _creation_counter=None)
        return super(NodeMeta, cls).construct(bases, attrs)


class Node(six.with_metaclass(NodeMeta, Interface)):

    @classmethod
    def require_get_node(cls):
        return cls == Node

    @classmethod
    def from_global_id(cls, global_id):
        return from_global_id(global_id)

    @classmethod
    def to_global_id(cls, type, id):
        return to_global_id(type, id)

    @classmethod
    def id_resolver(cls, root, args, context, info):
        return cls.to_global_id(info.parent_type.name, getattr(root, 'id', None))

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
            assert hasattr(object_type, 'get_node'), '{}.get_node method is required by the Node interface.'.format(object_type.__name__)

        return super(Node, cls).implements(object_type)
