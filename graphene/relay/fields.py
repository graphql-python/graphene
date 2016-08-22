import six
import functools

from graphql_relay.node.node import from_global_id

from ..core.fields import Field
from ..core.types.definitions import NonNull
from ..core.types.scalars import ID, Int, String
from ..utils.wrap_resolver_function import has_context, with_context
from .connection import Connection, Edge


def _is_thenable(obj):
    return callable(getattr(obj, "then", None))


class ConnectionField(Field):

    def __init__(self, type, resolver=None, description='',
                 connection_type=None, edge_type=None, **kwargs):
        super(
            ConnectionField,
            self).__init__(
            type,
            resolver=resolver,
            before=String(),
            after=String(),
            first=Int(),
            last=Int(),
            description=description,
            **kwargs)
        self.connection_type = connection_type or Connection
        self.edge_type = edge_type or Edge

    def _get_connection_type(self, connection_type, args, context, info, resolved):
        if isinstance(resolved, self.connection_type):
            return resolved
        return self.from_list(connection_type, resolved, args, context, info)

    @with_context
    def resolver(self, instance, args, context, info):
        schema = info.schema.graphene_schema
        connection_type = self.get_type(schema)

        resolver = super(ConnectionField, self).resolver
        if has_context(resolver):
            resolved = super(ConnectionField, self).resolver(instance, args, context, info)
        else:
            resolved = super(ConnectionField, self).resolver(instance, args, info)

        get_connection_type = functools.partial(self._get_connection_type, connection_type, args, context, info)

        if _is_thenable(resolved):
            return resolved.then(get_connection_type)

        return get_connection_type(resolved)

    def from_list(self, connection_type, resolved, args, context, info):
        return connection_type.from_list(resolved, args, context, info)

    def get_connection_type(self, node):
        return self.connection_type.for_node(node)

    def get_edge_type(self, node):
        return self.edge_type.for_node(node)

    def get_type(self, schema):
        type = schema.T(self.type)
        node = schema.objecttype(type)
        schema.register(node)
        connection_type = self.get_connection_type(node)

        return connection_type


class NodeField(Field):
    '''Fetches an object given its ID'''

    def __init__(self, object_type=None, *args, **kwargs):
        from graphene.relay.types import Node
        id = kwargs.pop('id', None) or ID(description='The ID of an object')
        super(NodeField, self).__init__(
            object_type or Node, id=id, *args, **kwargs)
        self.field_object_type = object_type

    def id_fetcher(self, global_id, context, info):
        from graphene.relay.utils import is_node
        schema = info.schema.graphene_schema
        try:
            _type, _id = from_global_id(global_id)
        except:
            return None
        object_type = schema.get_type(_type)
        if isinstance(self.field_object_type, six.string_types):
            field_object_type = schema.get_type(self.field_object_type)
        else:
            field_object_type = self.field_object_type
        if not is_node(object_type) or (self.field_object_type and object_type != field_object_type):
            return

        return object_type.get_node(_id, context, info)

    @with_context
    def resolver(self, instance, args, context, info):
        global_id = args.get('id')
        return self.id_fetcher(global_id, context, info)


class GlobalIDField(Field):
    '''The ID of an object'''

    def __init__(self, *args, **kwargs):
        super(GlobalIDField, self).__init__(NonNull(ID()), *args, **kwargs)

    def resolver(self, instance, args, info):
        return instance.to_global_id()
