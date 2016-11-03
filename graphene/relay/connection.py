import re
from collections import Iterable, OrderedDict
from functools import partial

import six

from graphql_relay import connection_from_list
from promise import Promise

from ..types import (AbstractType, Boolean, Enum, Int, Interface, List, NonNull, Scalar, String,
                     Union)
from ..types.field import Field
from ..types.objecttype import ObjectType, ObjectTypeMeta
from ..types.options import Options
from ..utils.is_base_type import is_base_type
from ..utils.props import props
from .node import is_node


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
            name=name,
            description=None,
            node=None,
        )
        options.interfaces = ()
        options.local_fields = OrderedDict()

        assert options.node, 'You have to provide a node in {}.Meta'.format(cls.__name__)
        assert issubclass(options.node, (Scalar, Enum, ObjectType, Interface, Union, NonNull)), (
            'Received incompatible node "{}" for Connection {}.'
        ).format(options.node, name)

        base_name = re.sub('Connection$', '', options.name) or options.node._meta.name
        if not options.name:
            options.name = '{}Connection'.format(base_name)

        edge_class = attrs.pop('Edge', None)

        class EdgeBase(AbstractType):
            node = Field(options.node, description='The item at the end of the edge')
            cursor = String(required=True, description='A cursor for use in pagination')

        edge_name = '{}Edge'.format(base_name)
        if edge_class and issubclass(edge_class, AbstractType):
            edge = type(edge_name, (EdgeBase, edge_class, ObjectType, ), {})
        else:
            edge_attrs = props(edge_class) if edge_class else {}
            edge = type(edge_name, (EdgeBase, ObjectType, ), edge_attrs)

        class ConnectionBase(AbstractType):
            page_info = Field(PageInfo, name='pageInfo', required=True)
            edges = NonNull(List(edge))

        bases = (ConnectionBase, ) + bases
        attrs = dict(attrs, _meta=options, Edge=edge)
        return ObjectTypeMeta.__new__(cls, name, bases, attrs)


class Connection(six.with_metaclass(ConnectionMeta, ObjectType)):

    @classmethod
    def Field(cls, *args, **kwargs):  # noqa: N802
        return ConnectionField(cls, *args, **kwargs)

    @classmethod
    def connection_resolver(cls, resolved, args, context, info):
        assert isinstance(resolved, Iterable), (
            'Resolved value from the connection field have to be iterable or instance of {}. '
            'Received "{}"'
        ).format(cls, resolved)
        connection = connection_from_list(
            resolved,
            args,
            connection_type=cls,
            edge_type=cls.Edge,
            pageinfo_type=PageInfo
        )
        connection.iterable = resolved
        return connection


class ConnectionField(Field):

    def __init__(self, type, *args, **kwargs):
        kwargs.setdefault('before', String())
        kwargs.setdefault('after', String())
        kwargs.setdefault('first', Int())
        kwargs.setdefault('last', Int())
        super(ConnectionField, self).__init__(
            type,
            *args,
            **kwargs
        )

    @property
    def type(self):
        type = super(ConnectionField, self).type
        assert issubclass(type, Connection), (
            '{} type have to be a subclass of Connection. Received "{}".'
        ).format(str(self), type)
        return type

    @classmethod
    def connection_resolver(cls, resolver, connection_type, root, args, context, info):
        resolved = resolver(root, args, context, info)

        if isinstance(resolved, connection_type):
            return resolved

        on_resolve = partial(connection_type.connection_resolver, args=args, context=context, info=info)
        if isinstance(resolved, Promise):
            return resolved.then(on_resolve)

        return on_resolve(resolved)

    def get_resolver(self, parent_resolver):
        resolver = super(ConnectionField, self).get_resolver(parent_resolver)
        return partial(self.connection_resolver, resolver, self.type)
