import six
from collections import OrderedDict
from functools import partial

from graphql_relay import from_global_id, to_global_id
from ..types import ObjectType, Interface, ID, Field
from ..types.interface import InterfaceMeta


def get_default_connection(cls):
    from .connection import Connection
    assert issubclass(cls, ObjectType), (
        'Can only get connection type on implemented Nodes.'
    )

    class Meta:
        node = cls

    return type('{}Connection'.format(cls.__name__), (Connection,), {'Meta': Meta})


class GlobalID(Field):
    def __init__(self, node, *args, **kwargs):
        super(GlobalID, self).__init__(ID, *args, **kwargs)
        self.node = node

    @staticmethod
    def id_resolver(parent_resolver, node, root, args, context, info):
        id = parent_resolver(root, args, context, info)
        # type_name = root._meta.name  # info.parent_type.name
        return node.to_global_id(info.parent_type.name, id)

    def get_resolver(self, parent_resolver):
        return partial(self.id_resolver, parent_resolver, self.node)


class NodeMeta(InterfaceMeta):

    def __new__(cls, name, bases, attrs):
        cls = InterfaceMeta.__new__(cls, name, bases, attrs)
        cls._meta.fields['id'] = GlobalID(cls, required=True, description='The ID of the object.')
        # new_fields = OrderedDict([
        #     ('id', GlobalID(cls, required=True, description='The ID of the object.'))
        # ])
        # new_fields.update(cls._meta.fields)
        # cls._meta.fields = new_fields
        return cls


class Node(six.with_metaclass(NodeMeta, Interface)):
    '''An object with an ID'''

    @classmethod
    def Field(cls):
        def resolve_node(root, args, context, info):
            return cls.get_node_from_global_id(args.get('id'), context, info)

        return Field(
            cls,
            description='The ID of the object',
            id=ID(required=True),
            resolver=resolve_node
        )

    @classmethod
    def get_node_from_global_id(cls, global_id, context, info):
        try:
            _type, _id = cls.from_global_id(global_id)
            graphene_type = info.schema.get_type(_type).graphene_type
            # We make sure the ObjectType implements the "Node" interface
            assert cls in graphene_type._meta.interfaces
        except:
            return None
        return graphene_type.get_node(_id, context, info)

    @classmethod
    def from_global_id(cls, global_id):
        return from_global_id(global_id)

    @classmethod
    def to_global_id(cls, type, id):
        return to_global_id(type, id)

    @classmethod
    def implements(cls, objecttype):
        require_get_node = cls.get_node_from_global_id == Node.get_node_from_global_id
        get_connection = getattr(objecttype, 'get_connection', None)
        if not get_connection:
            get_connection = partial(get_default_connection, objecttype)

        objecttype.Connection = get_connection()
        if require_get_node:
            assert hasattr(objecttype, 'get_node'), (
                '{}.get_node method is required by the Node interface.'
            ).format(objecttype.__name__)
