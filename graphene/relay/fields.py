import collections

from graphql_relay.connection.arrayconnection import (
    connectionFromArray
)
from graphql_relay.connection.connection import (
    connectionArgs
)
from graphql_relay.node.node import (
    globalIdField,
    fromGlobalId
)

from graphene.core.fields import Field, LazyNativeField, LazyField
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
                resolved, collections.Iterable), 'Resolved value from the connection field have to be iterable'
            return connectionFromArray(resolved, args)

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

    def get_field(self, schema):
        if self.field_object_type:
            field = NodeTypeField(self.field_object_type)
            field.contribute_to_class(self.object_type, self.field_name)
            return field.internal_field(schema)
        from graphene.relay.types import BaseNode
        return BaseNode.get_definitions(schema).nodeField


class NodeTypeField(LazyField):
    def __init__(self, object_type, *args, **kwargs):
        super(NodeTypeField, self).__init__(None, *args, **kwargs)
        self.field_object_type = object_type

    def inner_field(self, schema):
        from graphene.relay.types import BaseNode
        node_field = BaseNode.get_definitions(schema).nodeField

        def resolver(instance, args, info):
            global_id = args.get('id')
            resolved_global_id = fromGlobalId(global_id)
            if resolved_global_id.type == self.field_object_type._meta.type_name:
                return node_field.resolver(instance, args, info)

        args = {a.name: a for a in node_field.args}
        field = Field(self.field_object_type, id=args['id'], resolve=resolver)
        field.contribute_to_class(self.object_type, self.field_name)

        return field


class NodeIDField(LazyNativeField):
    def get_field(self, schema):
        return globalIdField(self.object_type._meta.type_name)
