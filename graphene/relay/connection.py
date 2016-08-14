import re
from collections import Iterable, OrderedDict
from functools import partial

import six

from graphql_relay import connection_from_list
from graphql_relay.connection.connection import connection_args

from ..types import Boolean, String, List
from ..types.field import Field
from ..types.objecttype import ObjectType, ObjectTypeMeta
from ..types.options import Options
from ..utils.is_base_type import is_base_type
from ..utils.props import props
from .node import Node

from ..types.utils import get_fields_in_type, yank_fields_from_attrs, merge_fields_in_attrs


def is_node(objecttype):
    for i in objecttype._meta.interfaces:
        if issubclass(i, Node):
            return True
    return False


class PageInfo(ObjectType):
    has_next_page = Boolean(
        required=True,
        name='hasNextPage',
        description='When paginating forwards, are there more items?',
    )

    has_previous_page = Boolean(
        required=True,
        name='hasPreviousPage',
        description='When paginating backwards, are there more items?',
    )

    start_cursor = String(
        name='startCursor',
        description='When paginating backwards, the cursor to continue.',
    )

    end_cursor = String(
        name='endCursor',
        description='When paginating forwards, the cursor to continue.',
    )


class ConnectionMeta(ObjectTypeMeta):

    def __new__(cls, name, bases, attrs):
        # Also ensure initialization is only performed for subclasses of Model
        # (excluding Model class itself).
        if not is_base_type(bases, ConnectionMeta):
            return type.__new__(cls, name, bases, attrs)

        options = Options(
            attrs.pop('Meta', None),
            name=None,
            description=None,
            node=None,
        )
        options.interfaces = ()

        assert options.node, 'You have to provide a node in {}.Meta'.format(cls.__name__)
        assert issubclass(options.node, (Node, ObjectType)), (
            'Received incompatible node "{}" for Connection {}.'
        ).format(options.node, name)

        base_name = re.sub('Connection$', '', name)
        if not options.name:
            options.name = '{}Connection'.format(base_name)


        edge_class = attrs.pop('Edge', None)
        edge_fields = OrderedDict([
            ('node', Field(options.node, description='The item at the end of the edge')),
            ('cursor', Field(String, required=True, description='A cursor for use in pagination'))
        ])
        edge_attrs = props(edge_class) if edge_class else OrderedDict()
        edge_fields.update(get_fields_in_type(ObjectType, edge_attrs))
        EdgeMeta = type('Meta', (object, ), {'fields': edge_fields})
        Edge = type('{}Edge'.format(base_name), (ObjectType,), {'Meta': EdgeMeta})

        options.local_fields = OrderedDict([
            ('page_info', Field(PageInfo, name='pageInfo', required=True)),
            ('edges', Field(List(Edge)))
        ])
        typed_fields = get_fields_in_type(ObjectType, attrs)
        options.local_fields.update(typed_fields)
        options.fields = options.local_fields
        yank_fields_from_attrs(attrs, typed_fields)

        return type.__new__(cls, name, bases, dict(attrs, _meta=options, Edge=Edge))


class Connection(six.with_metaclass(ConnectionMeta, ObjectType)):
    resolve_node = None
    resolve_cursor = None

    def __init__(self, *args, **kwargs):
        kwargs['pageInfo'] = kwargs.pop('pageInfo', kwargs.pop('page_info'))
        super(Connection, self).__init__(*args, **kwargs)


class IterableConnectionField(Field):

    def __init__(self, type, *args, **kwargs):
        # arguments = kwargs.pop('args', {})
        # if not arguments:
        #     arguments = connection_args
        # else:
        #     arguments = copy.copy(arguments)
        #     arguments.update(connection_args)

        super(IterableConnectionField, self).__init__(
            type,
            args=connection_args,
            *args,
            **kwargs
        )

    @property
    def connection(self):
        if is_node(self.type):
            connection_type = self.type.Connection
        else:
            connection_type = self.type
        assert issubclass(connection_type, Connection), (
            '{} type have to be a subclass of Connection'
        ).format(str(self))
        return connection_type

    @staticmethod
    def connection_resolver(resolver, connection, root, args, context, info):
        iterable = resolver(root, args, context, info)
        assert isinstance(iterable, Iterable), (
            'Resolved value from the connection field have to be iterable. '
            'Received "{}"'
        ).format(iterable)
        connection = connection_from_list(
            iterable,
            args,
            connection_type=connection,
            edge_type=connection.Edge,
        )
        return connection

    def get_resolver(self, parent_resolver):
        return partial(self.connection_resolver, parent_resolver, self.connection)

ConnectionField = IterableConnectionField
