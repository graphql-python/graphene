import re
from collections import Iterable
import six
from graphql_relay import connection_definitions, connection_from_list

from ..types.field import Field
from ..types.objecttype import ObjectType, ObjectTypeMeta

from ..utils.props import props

from ..types.field import Field, InputField
from ..utils.get_fields import get_fields
from ..utils.copy_fields import copy_fields
from ..utils.props import props


from ..types.objecttype import ObjectType

from ..utils.is_base_type import is_base_type
from ..types.options import Options


class ConnectionMeta(ObjectTypeMeta):

    def __new__(cls, name, bases, attrs):
        super_new = type.__new__

        # Also ensure initialization is only performed for subclasses of Model
        # (excluding Model class itself).
        if not is_base_type(bases, ConnectionMeta):
            return super_new(cls, name, bases, attrs)

        options = Options(
            attrs.pop('Meta', None),
            name=None,
            description=None,
            node=None,
            interfaces=[],
        )

        Edge = attrs.pop('Edge', None)
        edge_fields = props(Edge) if Edge else {}
        edge_fields = get_fields(ObjectType, edge_fields, ())

        connection_fields = copy_fields(Field, get_fields(ObjectType, attrs, bases))

        cls = super_new(cls, name, bases, dict(attrs, _meta=options))

        assert options.node, 'You have to provide a node in {}.Meta'.format(cls.__name__)
        from ..utils.get_graphql_type import get_graphql_type
        edge, connection = connection_definitions(
            name=options.name or re.sub('Connection$', '', cls.__name__),
            node_type=get_graphql_type(options.node),
            resolve_node=cls.resolve_node,
            resolve_cursor=cls.resolve_cursor,

            edge_fields=edge_fields,
            connection_fields=connection_fields,
        )
        cls.Edge = type(edge.name, (ObjectType, ), {'Meta': type('Meta', (object,), {'graphql_type': edge})})
        cls._meta.graphql_type = connection
        return cls


class Connection(six.with_metaclass(ConnectionMeta, ObjectType)):
    resolve_node = None
    resolve_cursor = None


class IterableConnectionField(Field):
    # def __init__(self, type, *args, **kwargs):
    #     if 

    def resolver(self, root, args, context, info):
        iterable = super(ConnectionField, self).resolver(root, args, context, info)
        # if isinstance(resolved, self.type.graphene)
        assert isinstance(
            iterable, Iterable), 'Resolved value from the connection field have to be iterable'
        connection = connection_from_list(
            iterable,
            args,
            connection_type=None,
            edge_type=None,
            pageinfo_type=None
        )
        return connection


ConnectionField = IterableConnectionField
