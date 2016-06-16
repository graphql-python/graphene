from functools import partial

import six

from graphql_relay import from_global_id, node_definitions, to_global_id

from ..types.field import Field
from ..types.interface import Interface
from ..types.objecttype import ObjectType, ObjectTypeMeta
from ..types.options import Options
from .connection import Connection


class NodeMeta(ObjectTypeMeta):

    def __new__(cls, name, bases, attrs):
        cls = super(NodeMeta, cls).__new__(cls, name, bases, attrs)
        is_object_type = cls.is_object_type()
        if not is_object_type:
            get_node_from_global_id = getattr(cls, 'get_node_from_global_id', None)
            id_resolver = getattr(cls, 'id_resolver', None)
            assert get_node_from_global_id, '{}.get_node_from_global_id method is required by the Node interface.'.format(cls.__name__)
            node_interface, node_field = node_definitions(
                get_node_from_global_id,
                id_resolver=id_resolver,
            )
            cls._meta = Options(None, graphql_type=node_interface)
            cls.Field = partial(
                Field.copy_and_extend,
                node_field,
                type=node_field.type,
                parent=cls,
                _creation_counter=None)
        else:
            # The interface provided by node_definitions is not an instance
            # of GrapheneInterfaceType, so it will have no graphql_type,
            # so will not trigger Node.implements
            cls.implements(cls)
        return cls


class Node(six.with_metaclass(NodeMeta, Interface)):
    _connection = None

    @classmethod
    def require_get_node(cls):
        return Node._meta.graphql_type in cls._meta.graphql_type._provided_interfaces

    @classmethod
    def from_global_id(cls, global_id):
        if cls is Node:
            return from_global_id(global_id)
        raise NotImplementedError("You need to implement {}.from_global_id".format(cls.__name__))

    @classmethod
    def to_global_id(cls, type, id):
        if cls is Node:
            return to_global_id(type, id)
        raise NotImplementedError("You need to implement {}.to_global_id".format(cls.__name__))

    @classmethod
    def id_resolver(cls, root, args, context, info):
        return cls.to_global_id(info.parent_type.name, getattr(root, 'id', None))

    @classmethod
    def get_node_from_global_id(cls, global_id, context, info):
        try:
            _type, _id = cls.from_global_id(global_id)
        except:
            return None
        graphql_type = info.schema.get_type(_type)
        if cls._meta.graphql_type not in graphql_type.get_interfaces():
            return
        return graphql_type.graphene_type.get_node(_id, context, info)

    @classmethod
    def get_default_connection(cls):
        assert issubclass(cls, ObjectType), 'Can only get connection type on implemented Nodes.'
        if not cls._connection:
            class Meta:
                node = cls
            cls._connection = type('{}Connection'.format(cls.__name__), (Connection,), {'Meta': Meta})
        return cls._connection

    @classmethod
    def implements(cls, object_type):
        '''
        We check here that the object_type have the required get_node method
        in it
        '''
        if cls.require_get_node():
            assert hasattr(
                object_type, 'get_node'), '{}.get_node method is required by the Node interface.'.format(
                object_type.__name__)

        return super(Node, cls).implements(object_type)
