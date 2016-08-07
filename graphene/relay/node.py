from functools import partial

import six

from graphql_relay import from_global_id, node_definitions, to_global_id

from ..types.field import Field
from ..types.interface import Interface
from ..types.objecttype import ObjectType, ObjectTypeMeta
from ..types.options import Options
from ..utils.copy_fields import copy_fields
from .connection import Connection


# We inherit from ObjectTypeMeta as we want to allow
# inheriting from Node, and also ObjectType.
# Like class MyNode(Node): pass
# And class MyNodeImplementation(Node, ObjectType): pass
class NodeMeta(ObjectTypeMeta):

    @staticmethod
    def _get_interface_options(meta):
        return Options(
            meta,
        )

    @staticmethod
    def _create_objecttype(cls, name, bases, attrs):
        cls = super(NodeMeta, cls)._create_objecttype(cls, name, bases, attrs)
        require_get_node = Node._meta.graphql_type in cls._meta.graphql_type._provided_interfaces
        if require_get_node:
            assert hasattr(
                cls, 'get_node'), '{}.get_node method is required by the Node interface.'.format(
                cls.__name__)

        return cls

    @staticmethod
    def _create_interface(cls, name, bases, attrs):
        options = cls._get_interface_options(attrs.pop('Meta', None))
        cls = type.__new__(cls, name, bases, dict(attrs, _meta=options))
        get_node_from_global_id = getattr(cls, 'get_node_from_global_id', None)
        id_resolver = getattr(cls, 'id_resolver', None)
        assert get_node_from_global_id, '{}.get_node_from_global_id method is required by the Node interface.'.format(
            cls.__name__)
        node_interface, node_field = node_definitions(
            get_node_from_global_id,
            id_resolver=id_resolver,
            type_resolver=cls.resolve_type,
        )
        options.graphql_type = node_interface

        fields = copy_fields(Field, options.graphql_type.get_fields(), parent=cls)
        options.get_fields = lambda: fields

        cls.Field = partial(
            Field.copy_and_extend,
            node_field,
            type=node_field.type,
            parent=cls,
            _creation_counter=None)

        return cls


class Node(six.with_metaclass(NodeMeta, Interface)):
    _connection = None
    resolve_type = None

    @classmethod
    def from_global_id(cls, global_id):
        return from_global_id(global_id)

    @classmethod
    def to_global_id(cls, type, id):
        return to_global_id(type, id)

    @classmethod
    def resolve_id(cls, root, args, context, info):
        return getattr(root, 'id', None)

    @classmethod
    def id_resolver(cls, root, args, context, info):
        return cls.to_global_id(info.parent_type.name, cls.resolve_id(root, args, context, info))

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
