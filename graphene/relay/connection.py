import re
from collections import Iterable, OrderedDict
from functools import partial

from ..types import Boolean, Enum, Int, Interface, List, NonNull, Scalar, String, Union
from ..types.field import Field
from ..types.objecttype import ObjectType, ObjectTypeOptions
from ..utils.thenables import maybe_thenable
from ..utils import base64, is_str, unbase64
from .node import is_node

from .connectiontypes import ConnectionType, PageInfoType, EdgeType


def connection_from_list(data, args=None, **kwargs):
    '''
    A simple function that accepts an array and connection arguments, and returns
    a connection object for use in GraphQL. It uses array offsets as pagination,
    so pagination will only work if the array is static.
    '''
    _len = len(data)
    return connection_from_list_slice(
        data,
        args,
        slice_start=0,
        list_length=_len,
        list_slice_length=_len,
        **kwargs
    )


def connection_from_list_slice(list_slice, args=None, connection_type=None,
                               edge_type=None, pageinfo_type=None,
                               slice_start=0, list_length=0, list_slice_length=None):
    '''
    Given a slice (subset) of an array, returns a connection object for use in
    GraphQL.
    This function is similar to `connectionFromArray`, but is intended for use
    cases where you know the cardinality of the connection, consider it too large
    to materialize the entire array, and instead wish pass in a slice of the
    total result large enough to cover the range specified in `args`.
    '''
    connection_type = connection_type or Connection
    edge_type = edge_type or Edge
    pageinfo_type = pageinfo_type or PageInfo

    args = args or {}

    before = args.get('before')
    after = args.get('after')
    first = args.get('first')
    last = args.get('last')
    if list_slice_length is None:
        list_slice_length = len(list_slice)
    slice_end = slice_start + list_slice_length
    before_offset = get_offset_with_default(before, list_length)
    after_offset = get_offset_with_default(after, -1)

    start_offset = max(
        slice_start - 1,
        after_offset,
        -1
    ) + 1
    end_offset = min(
        slice_end,
        before_offset,
        list_length
    )
    if isinstance(first, int):
        end_offset = min(
            end_offset,
            start_offset + first
        )
    if isinstance(last, int):
        start_offset = max(
            start_offset,
            end_offset - last
        )

    # If supplied slice is too large, trim it down before mapping over it.
    _slice = list_slice[
        max(start_offset - slice_start, 0):
        list_slice_length - (slice_end - end_offset)
    ]
    edges = [
        edge_type(
            node=node,
            cursor=offset_to_cursor(start_offset + i)
        )
        for i, node in enumerate(_slice)
    ]


    first_edge_cursor = edges[0].cursor if edges else None
    last_edge_cursor = edges[-1].cursor if edges else None
    lower_bound = after_offset + 1 if after else 0
    upper_bound = before_offset if before else list_length

    return connection_type(
        edges=edges,
        page_info=pageinfo_type(
            start_cursor=first_edge_cursor,
            end_cursor=last_edge_cursor,
            has_previous_page=isinstance(last, int) and start_offset > lower_bound,
            has_next_page=isinstance(first, int) and end_offset < upper_bound
        )
    )


def offset_to_cursor(offset):
    '''
    Creates the cursor string from an offset.
    '''
    return base64(PREFIX + str(offset))


def cursor_to_offset(cursor):
    '''
    Rederives the offset from the cursor string.
    '''
    try:
        return int(unbase64(cursor)[len(PREFIX):])
    except:
        return None


def cursor_for_object_in_connection(data, _object):
    '''
    Return the cursor associated with an object in an array.
    '''
    if _object not in data:
        return None

    offset = data.index(_object)
    return offset_to_cursor(offset)


def get_offset_with_default(cursor=None, default_offset=0):
    '''
    Given an optional cursor and a default offset, returns the offset
    to use; if the cursor contains a valid offset, that will be used,
    otherwise it will be the default.
    '''
    if not is_str(cursor):
        return default_offset

    offset = cursor_to_offset(cursor)
    try:
        return int(offset)
    except:
        return default_offset



class PageInfo(ObjectType):
    class Meta:
        description = (
            "The Relay compliant `PageInfo` type, containing data necessary to"
            " paginate this connection."
        )

    has_next_page = Boolean(
        required=True,
        name="hasNextPage",
        description="When paginating forwards, are there more items?",
    )

    has_previous_page = Boolean(
        required=True,
        name="hasPreviousPage",
        description="When paginating backwards, are there more items?",
    )

    start_cursor = String(
        name="startCursor",
        description="When paginating backwards, the cursor to continue.",
    )

    end_cursor = String(
        name="endCursor",
        description="When paginating forwards, the cursor to continue.",
    )


class ConnectionOptions(ObjectTypeOptions):
    node = None


class Connection(ObjectType):
    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(cls, node=None, name=None, **options):
        _meta = ConnectionOptions(cls)
        assert node, "You have to provide a node in {}.Meta".format(cls.__name__)
        assert isinstance(node, NonNull) or issubclass(
            node, (Scalar, Enum, ObjectType, Interface, Union, NonNull)
        ), ('Received incompatible node "{}" for Connection {}.').format(
            node, cls.__name__
        )

        base_name = re.sub("Connection$", "", name or cls.__name__) or node._meta.name
        if not name:
            name = "{}Connection".format(base_name)

        edge_class = getattr(cls, "Edge", None)
        _node = node

        class EdgeBase(object):
            node = Field(_node, description="The item at the end of the edge")
            cursor = String(required=True, description="A cursor for use in pagination")

        class EdgeMeta:
            description = "A Relay edge containing a `{}` and its cursor.".format(
                base_name
            )

        edge_name = "{}Edge".format(base_name)
        if edge_class:
            edge_bases = (edge_class, EdgeBase, ObjectType)
        else:
            edge_bases = (EdgeBase, ObjectType)

        edge = type(edge_name, edge_bases, {"Meta": EdgeMeta})
        cls.Edge = edge

        options["name"] = name
        _meta.node = node
        _meta.fields = OrderedDict(
            [
                (
                    "page_info",
                    Field(
                        PageInfo,
                        name="pageInfo",
                        required=True,
                        description="Pagination data for this connection.",
                    ),
                ),
                (
                    "edges",
                    Field(
                        NonNull(List(edge)),
                        description="Contains the nodes in this connection.",
                    ),
                ),
            ]
        )
        return super(Connection, cls).__init_subclass_with_meta__(
            _meta=_meta, **options
        )


class IterableConnectionField(Field):
    def __init__(self, type, *args, **kwargs):
        kwargs.setdefault("before", String())
        kwargs.setdefault("after", String())
        kwargs.setdefault("first", Int())
        kwargs.setdefault("last", Int())
        super(IterableConnectionField, self).__init__(type, *args, **kwargs)

    @property
    def type(self):
        type = super(IterableConnectionField, self).type
        connection_type = type
        if isinstance(type, NonNull):
            connection_type = type.of_type

        if is_node(connection_type):
            raise Exception(
                "ConnectionFields now need a explicit ConnectionType for Nodes.\n"
                "Read more: https://github.com/graphql-python/graphene/blob/v2.0.0/UPGRADE-v2.0.md#node-connections"
            )

        assert issubclass(connection_type, Connection), (
            '{} type have to be a subclass of Connection. Received "{}".'
        ).format(self.__class__.__name__, connection_type)
        return type

    @classmethod
    def resolve_connection(cls, connection_type, args, resolved):
        if isinstance(resolved, connection_type):
            return resolved

        assert isinstance(resolved, Iterable), (
            "Resolved value from the connection field have to be iterable or instance of {}. "
            'Received "{}"'
        ).format(connection_type, resolved)
        connection = connection_from_list(
            resolved,
            args,
            connection_type=connection_type,
            edge_type=connection_type.Edge,
            pageinfo_type=PageInfo,
        )
        connection.iterable = resolved
        return connection

    @classmethod
    def connection_resolver(cls, resolver, connection_type, root, info, **args):
        resolved = resolver(root, info, **args)

        if isinstance(connection_type, NonNull):
            connection_type = connection_type.of_type

        on_resolve = partial(cls.resolve_connection, connection_type, args)
        return maybe_thenable(resolved, on_resolve)

    def get_resolver(self, parent_resolver):
        resolver = super(IterableConnectionField, self).get_resolver(parent_resolver)
        return partial(self.connection_resolver, resolver, self.type)


ConnectionField = IterableConnectionField
