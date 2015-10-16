from collections import Iterable, OrderedDict

from graphql_relay.connection.arrayconnection import (
    connection_from_list
)
from graphql_relay.connection.connection import (
    connectionArgs
)
from graphql_relay.node.node import (
    global_id_field,
    to_global_id,
    from_global_id
)

from graphene.core.fields import Field, LazyNativeField, IDField
from graphene.utils import cached_property
from graphene.utils import memoize


class ConnectionField(Field):

    def __init__(self, field_type, resolve=None, description=''):
        super(ConnectionField, self).__init__(field_type, resolve=resolve,
                                              args=connectionArgs, description=description)

    def wrap_resolved(self, value, instance, args, info):
        return value

    def resolve(self, instance, args, info):
        resolved = super(ConnectionField, self).resolve(instance, args, info)
        if resolved:
            resolved = self.wrap_resolved(resolved, instance, args, info)
            assert isinstance(
                resolved, Iterable), 'Resolved value from the connection field have to be iterable'
            return connection_from_list(resolved, args)

    @memoize
    def internal_type(self, schema):
        from graphene.relay.types import BaseNode
        object_type = self.get_object_type(schema)
        assert issubclass(
            object_type, BaseNode), 'Only nodes have connections.'
        return object_type.get_connection(schema)


class NodeField(LazyNativeField):
    def __init__(self, object_type=None, *args, **kwargs):
        super(NodeField, self).__init__(*args, **kwargs)
        self.field_object_type = object_type

    def get_object_type_field(self, schema):
        from graphene.relay.types import BaseNode
        node_field = BaseNode.get_definitions(schema).node_field

        def resolver(instance, args, info):
            global_id = args.get('id')
            resolved_global_id = from_global_id(global_id)
            if resolved_global_id.type == self.field_object_type._meta.type_name:
                return node_field.resolver(instance, args, info)

        args = OrderedDict(node_field.args.items())
        field = Field(self.field_object_type, id=args['id'], resolve=resolver)
        field.contribute_to_class(self.object_type, self.field_name)

        return field.internal_field(schema)

    def get_field(self, schema):
        if self.field_object_type:
            return self.get_object_type_field(schema)
        from graphene.relay.types import BaseNode
        return BaseNode.get_definitions(schema).node_field


class NodeIDField(IDField):
    required = True

    def resolve(self, instance, args, info):
        type_name = self.object_type._meta.type_name
        return to_global_id(type_name, instance.id)
