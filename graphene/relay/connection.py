import re
import copy
from functools import partial
import six
from graphql_relay import connection_definitions

from ..types.field import Field
from ..types.mutation import Mutation, MutationMeta
from ..types.interface import GrapheneInterfaceType, Interface, InterfaceTypeMeta
from ..types.objecttype import ObjectType, ObjectTypeMeta

from ..utils.props import props


class ConnectionMeta(ObjectTypeMeta):

    def get_options(cls, meta):
        options = cls.options_class(
            meta,
            name=None,
            description=None,
            node=None,
            interfaces=[],
            abstract=False
        )
        options.graphql_type = None
        return options

    def construct(cls, bases, attrs):
        if not cls._meta.abstract:
            Edge = attrs.pop('Edge', None)
            edge_fields = props(Edge) if Edge else {}

            edge_fields = {f.name: f for f in ObjectType._extract_local_fields(edge_fields)}
            local_fields = cls._extract_local_fields(attrs)

        cls = super(ConnectionMeta, cls).construct(bases, attrs)
        if not cls._meta.abstract:
            from ..utils.get_graphql_type import get_graphql_type
            assert cls._meta.node, 'You have to provide a node in {}.Meta'.format(cls.__name__)
            edge, connection = connection_definitions(
                name=cls._meta.name or re.sub('Connection$', '', cls.__name__),
                node_type=get_graphql_type(cls._meta.node),
                resolve_node=cls.resolve_node,
                resolve_cursor=cls.resolve_cursor,

                edge_fields=edge_fields,
                connection_fields=local_fields,
            )
            cls._meta.graphql_type = connection
        return cls



class Connection(six.with_metaclass(ConnectionMeta, ObjectType)):
    class Meta:
        abstract = True

    resolve_node = None
    resolve_cursor = None
