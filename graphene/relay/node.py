from functools import partial

import six

from graphql_relay import from_global_id, to_global_id

from ..types import ID, Field, Interface, ObjectType
from ..types.interface import InterfaceMeta


def is_node(objecttype):
    '''
    Check if the given objecttype has Node as an interface
    '''
    assert issubclass(objecttype, ObjectType), (
        'Only ObjectTypes can have a Node interface. Received %s'
    ) % objecttype
    for i in objecttype._meta.interfaces:
        if issubclass(i, Node):
            return True
    return False


class GlobalID(Field):

    def __init__(self, node=None, required=True, *args, **kwargs):
        super(GlobalID, self).__init__(ID, required=required, *args, **kwargs)
        self.node = node or Node

    @staticmethod
    def id_resolver(parent_resolver, node, root, args, context, info):
        id = parent_resolver(root, args, context, info)
        return node.to_global_id(info.parent_type.name, id)  # root._meta.name

    def get_resolver(self, parent_resolver):
        return partial(self.id_resolver, parent_resolver, self.node)


class NodeMeta(InterfaceMeta):

    def __new__(cls, name, bases, attrs):
        cls = InterfaceMeta.__new__(cls, name, bases, attrs)
        cls._meta.fields['id'] = GlobalID(cls, description='The ID of the object.')
        return cls


class NodeField(Field):

    def __init__(self, node, type=False, deprecation_reason=None,
                 name=None, **kwargs):
        assert issubclass(node, Node), 'NodeField can only operate in Nodes'
        type = type or node
        super(NodeField, self).__init__(
            type,
            description='The ID of the object',
            id=ID(required=True),
            resolver=node.node_resolver
        )


class Node(six.with_metaclass(NodeMeta, Interface)):
    '''An object with an ID'''

    @classmethod
    def Field(cls, *args, **kwargs):  # noqa: N802
        return NodeField(cls, *args, **kwargs)

    @classmethod
    def node_resolver(cls, root, args, context, info):
        return cls.get_node_from_global_id(args.get('id'), context, info)

    @classmethod
    def get_node_from_global_id(cls, global_id, context, info):
        try:
            _type, _id = cls.from_global_id(global_id)
            graphene_type = info.schema.get_type(_type).graphene_type
            # We make sure the ObjectType implements the "Node" interface
            assert cls in graphene_type._meta.interfaces
        except:
            return None
        get_node = getattr(graphene_type, 'get_node', None)
        if get_node:
            return get_node(_id, context, info)

    @classmethod
    def from_global_id(cls, global_id):
        return from_global_id(global_id)

    @classmethod
    def to_global_id(cls, type, id):
        return to_global_id(type, id)
