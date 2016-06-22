import re
import copy
from collections import Iterable, OrderedDict

import six

from graphql_relay import connection_definitions, connection_from_list
from graphql_relay.connection.connection import connection_args

from ..types.field import Field
from ..types.objecttype import ObjectType, ObjectTypeMeta
from ..types.options import Options
from ..utils.copy_fields import copy_fields
from ..utils.get_fields import get_fields
from ..utils.is_base_type import is_base_type
from ..utils.props import props


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
        fields = copy_fields(Field, options.graphql_type.get_fields(), parent=cls)

        cls._meta.get_fields = lambda: fields

        return cls


class Connection(six.with_metaclass(ConnectionMeta, ObjectType)):
    resolve_node = None
    resolve_cursor = None

    def __init__(self, *args, **kwargs):
        kwargs['pageInfo'] = kwargs.pop('pageInfo', kwargs.pop('page_info'))
        super(Connection, self).__init__(*args, **kwargs)


class IterableConnectionField(Field):

    def __init__(self, type, *other_args, **kwargs):
        args = kwargs.pop('args', {})
        if not args:
            args = connection_args
        else:
            args = copy.copy(args)
            args.update(connection_args)

        super(IterableConnectionField, self).__init__(type, args=args, *other_args, **kwargs)

    @property
    def type(self):
        from ..utils.get_graphql_type import get_graphql_type
        return get_graphql_type(self.connection)

    @type.setter
    def type(self, value):
        self._type = value

    @property
    def connection(self):
        from .node import Node
        graphql_type = super(IterableConnectionField, self).type
        if issubclass(graphql_type.graphene_type, Node):
            connection_type = graphql_type.graphene_type.get_default_connection()
        else:
            connection_type = graphql_type.graphene_type
        assert issubclass(connection_type, Connection), '{} type have to be a subclass of Connection'.format(str(self))
        return connection_type

    def connection_resolver(self, root, args, context, info):
        iterable = super(ConnectionField, self).resolver(root, args, context, info)
        # if isinstance(resolved, self.type.graphene)
        assert isinstance(
            iterable, Iterable), 'Resolved value from the connection field have to be iterable. Received "{}"'.format(iterable)
        connection = connection_from_list(
            iterable,
            args,
            connection_type=self.connection,
            edge_type=self.connection.Edge,
        )
        return connection

    @property
    def resolver(self):
        return self.connection_resolver

    @resolver.setter
    def resolver(self, resolver):
        self._resolver = resolver

ConnectionField = IterableConnectionField
