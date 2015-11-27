from graphql_relay.node.node import from_global_id

from ..core.fields import Field
from ..core.types.definitions import NonNull
from ..core.types.scalars import ID, Int, String


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
        self.connection_type = connection_type
        self.edge_type = edge_type

    def wrap_resolved(self, value, instance, args, info):
        return value

    def resolver(self, instance, args, info):
        schema = info.schema.graphene_schema
        connection_type = self.get_type(schema)
        resolved = super(ConnectionField, self).resolver(instance, args, info)
        if isinstance(resolved, connection_type):
            return resolved
        return connection_type.from_list(resolved, args, info)

    def get_connection_type(self, node):
        connection_type = self.connection_type or node.get_connection_type()
        edge_type = self.get_edge_type(node)
        return connection_type.for_node(node, edge_type=edge_type)

    def get_edge_type(self, node):
        edge_type = self.edge_type or node.get_edge_type()
        return edge_type.for_node(node)

    def get_type(self, schema):
        from graphene.relay.utils import is_node
        type = schema.T(self.type)
        node = schema.objecttype(type)
        assert is_node(node), 'Only nodes have connections.'
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

    def id_fetcher(self, global_id, info):
        from graphene.relay.utils import is_node
        schema = info.schema.graphene_schema
        try:
            resolved_global_id = from_global_id(global_id)
        except:
            return None
        _type, _id = resolved_global_id.type, resolved_global_id.id
        object_type = schema.get_type(_type)
        if not is_node(object_type) or (self.field_object_type and
                                        object_type != self.field_object_type):
            return

        return object_type.get_node(_id, info)

    def resolver(self, instance, args, info):
        global_id = args.get('id')
        return self.id_fetcher(global_id, info)


class GlobalIDField(Field):
    '''The ID of an object'''

    def __init__(self, *args, **kwargs):
        super(GlobalIDField, self).__init__(NonNull(ID()), *args, **kwargs)

    def contribute_to_class(self, cls, name):
        from graphene.relay.utils import is_node, is_node_type
        in_node = is_node(cls) or is_node_type(cls)
        assert in_node, 'GlobalIDField could only be inside a Node, but got %r' % cls
        super(GlobalIDField, self).contribute_to_class(cls, name)

    def resolver(self, instance, args, info):
        return instance.to_global_id()
