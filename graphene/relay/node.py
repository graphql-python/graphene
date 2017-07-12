from functools import partial

import six

from graphql_relay import from_global_id, to_global_id

from ..types import ID, Field, Interface, ObjectType
from ..types.utils import get_type
from ..types.interface import InterfaceOptions


def is_node(objecttype):
    '''
    Check if the given objecttype has Node as an interface
    '''
    if not issubclass(objecttype, ObjectType):
        return False

    for i in objecttype._meta.interfaces:
        if issubclass(i, Node):
            return True
    return False


class GlobalID(Field):

    def __init__(self, node=None, parent_type=None, required=True, *args, **kwargs):
        super(GlobalID, self).__init__(ID, required=required, *args, **kwargs)
        self.node = node or Node
        self.parent_type_name = parent_type._meta.name if parent_type else None

    @staticmethod
    def id_resolver(parent_resolver, node, root, args, context, info, parent_type_name=None):
        type_id = parent_resolver(root, args, context, info)
        parent_type_name = parent_type_name or info.parent_type.name
        return node.to_global_id(parent_type_name, type_id)  # root._meta.name

    def get_resolver(self, parent_resolver):
        return partial(self.id_resolver, parent_resolver, self.node, parent_type_name=self.parent_type_name)


class NodeField(Field):

    def __init__(self, node, type=False, deprecation_reason=None,
                 name=None, **kwargs):
        assert issubclass(node, Node), 'NodeField can only operate in Nodes'
        self.node_type = node
        self.field_type = type

        super(NodeField, self).__init__(
            # If we don's specify a type, the field type will be the node interface
            type or node,
            description='The ID of the object',
            id=ID(required=True)
        )

    def get_resolver(self, parent_resolver):
        return partial(self.node_type.node_resolver, only_type=get_type(self.field_type))


class Node(Interface):
    '''An object with an ID'''

    def __init_subclass_with_meta__(cls, **options):
        _meta = InterfaceOptions(cls)
        _meta.fields = {
            'id': GlobalID(cls, description='The ID of the object.')
        }
        super(Node, cls).__init_subclass_with_meta__(cls, _meta=_meta, **options)

    @classmethod
    def Field(cls, *args, **kwargs):  # noqa: N802
        return NodeField(cls, *args, **kwargs)

    @classmethod
    def node_resolver(cls, root, args, context, info, only_type=None):
        return cls.get_node_from_global_id(args.get('id'), context, info, only_type)

    @classmethod
    def get_node_from_global_id(cls, global_id, context, info, only_type=None):
        try:
            _type, _id = cls.from_global_id(global_id)
            graphene_type = info.schema.get_type(_type).graphene_type
        except:
            return None

        if only_type:
            assert graphene_type == only_type, (
                'Must receive an {} id.'
            ).format(graphene_type._meta.name)

        # We make sure the ObjectType implements the "Node" interface
        if cls not in graphene_type._meta.interfaces:
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
