import re
from collections import Iterable, OrderedDict
from functools import partial

from promise import Promise
import six

from graphql_relay import connection_from_list

from ..types import Boolean, Int, List, String, AbstractType, Dynamic
from ..types.field import Field
from ..types.objecttype import ObjectType, ObjectTypeMeta
from ..types.options import Options
from ..utils.is_base_type import is_base_type
from ..utils.props import props
from .node import Node


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
        options.local_fields = OrderedDict()
        base_name = re.sub('Connection$', '', name)

        if attrs.get('edges'):
            edges = attrs.get('edges')
            edge = edges.of_type
        else:
            assert options.node, 'You have to provide a node in {}.Meta'.format(cls.__name__)
            assert issubclass(options.node, (Node, ObjectType)), (
                'Received incompatible node "{}" for Connection {}.'
            ).format(options.node, name)

            base_name = re.sub('Connection$', '', name)

            edge_class = attrs.pop('Edge', None)

            edge_attrs = {
                'node': Field(
                    options.node, description='The item at the end of the edge'),
                'cursor': Edge._meta.fields['cursor']
            }

            edge_name = '{}Edge'.format(base_name)
            if edge_class and issubclass(edge_class, AbstractType):
                edge = type(edge_name, (edge_class, ObjectType, ), edge_attrs)
            else:
                additional_attrs = props(edge_class) if edge_class else {}
                edge_attrs.update(additional_attrs)
                edge = type(edge_name, (ObjectType, ), edge_attrs)

            edges = List(edge)

        if not options.name:
            options.name = '{}Connection'.format(base_name)

        attrs.update({
            'page_info': Field(PageInfo, name='pageInfo', required=True),
            'edges': edges,
        })
        attrs = dict(attrs, _meta=options, Edge=edge)
        return ObjectTypeMeta.__new__(cls, name, bases, attrs)


class Connection(six.with_metaclass(ConnectionMeta, ObjectType)):

    @classmethod
    def for_type(cls, gql_type):
        connection_name = '{}Connection'.format(gql_type._meta.name)

        class Meta(object):
            node = gql_type

        return type(connection_name, (Connection, ), {'Meta': Meta})


class Edge(AbstractType):
    cursor = String(required=True, description='A cursor for use in pagination')


def is_connection(gql_type):
    '''Checks if a type is a connection. Taken directly from the spec definition:
    https://facebook.github.io/relay/graphql/connections.htm#sec-Connection-Types'''
    return gql_type._meta.name.endswith('Connection') if hasattr(gql_type, '_meta') else False


class IterableConnectionField(Field):

    def __init__(self, gql_type, *args, **kwargs):
        assert is_connection(gql_type) or isinstance(gql_type, Dynamic), (
            'The provided type "{}" for this ConnectionField has to be a Connection as defined by the Relay'
            ' spec.'.format(gql_type)
        )
        super(IterableConnectionField, self).__init__(
            gql_type,
            *args,
            before=String(),
            after=String(),
            first=Int(),
            last=Int(),
            **kwargs
        )

    @property
    def type(self):
        gql_type = super(IterableConnectionField, self).type
        if isinstance(gql_type, Dynamic):
            return gql_type.get_type()
        else:
            return gql_type

    @staticmethod
    def connection_resolver(resolver, connection, root, args, context, info):
        resolved = Promise.resolve(resolver(root, args, context, info))

        def handle_connection_and_list(result):
            if isinstance(result, connection):
                return result
            elif is_connection(result):
                raise AssertionError('Resolved value from the connection field has to be a {}. '
                                     'Received {}.'.format(connection, type(result)))
            else:
                assert isinstance(result, Iterable), (
                    'Resolved value from the connection field have to be iterable. '
                    'Received "{}"'
                ).format(result)

                resolved_connection = connection_from_list(
                    result,
                    args,
                    connection_type=connection,
                    edge_type=connection.Edge,
                    pageinfo_type=PageInfo
                )
                resolved_connection.iterable = result
                return resolved_connection

        return resolved.then(handle_connection_and_list)

    def get_resolver(self, parent_resolver):
        resolver = super(IterableConnectionField, self).get_resolver(parent_resolver)
        return partial(self.connection_resolver, resolver, self.type)

ConnectionField = IterableConnectionField
