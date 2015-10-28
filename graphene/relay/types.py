from graphql_relay.node.node import (
    to_global_id
)

from graphene.core.types import Interface, ObjectType, Mutation, InputObjectType
from graphene.core.fields import BooleanField, StringField, ListField, Field
from graphene.relay.fields import GlobalIDField
from graphene.utils import memoize


class PageInfo(ObjectType):
    has_next_page = BooleanField(required=True, description='When paginating forwards, are there more items?')
    has_previous_page = BooleanField(required=True, description='When paginating backwards, are there more items?')
    start_cursor = StringField(description='When paginating backwards, the cursor to continue.')
    end_cursor = StringField(description='When paginating forwards, the cursor to continue.')


class Edge(ObjectType):
    '''An edge in a connection.'''
    class Meta:
        type_name = 'DefaultEdge'

    node = Field(lambda field: field.object_type.node_type, description='The item at the end of the edge')
    cursor = StringField(required=True, description='A cursor for use in pagination')

    @classmethod
    @memoize
    def for_node(cls, node):
        from graphene.relay.utils import is_node
        assert is_node(node), 'ObjectTypes in a edge have to be Nodes'
        return type('%s%s' % (node._meta.type_name, cls._meta.type_name), (cls, ), {'node_type': node})


class Connection(ObjectType):
    '''A connection to a list of items.'''
    class Meta:
        type_name = 'DefaultConnection'

    page_info = Field(PageInfo, required=True, description='The Information to aid in pagination')
    edges = ListField(lambda field: field.object_type.edge_type, description='Information to aid in pagination.')

    _connection_data = None

    @classmethod
    @memoize
    def for_node(cls, node, edge_type=None):
        from graphene.relay.utils import is_node
        edge_type = edge_type or Edge
        assert is_node(node), 'ObjectTypes in a connection have to be Nodes'
        return type('%s%s' % (node._meta.type_name, cls._meta.type_name), (cls, ), {'edge_type': edge_type.for_node(node)})

    def set_connection_data(self, data):
        self._connection_data = data

    def get_connection_data(self):
        return self._connection_data


class BaseNode(object):
    @classmethod
    def _prepare_class(cls):
        from graphene.relay.utils import is_node
        if is_node(cls):
            assert hasattr(
                cls, 'get_node'), 'get_node classmethod not found in %s Node' % cls

    @classmethod
    def to_global_id(cls, instance, args, info):
        type_name = cls._meta.type_name
        return to_global_id(type_name, instance.id)

    connection_type = Connection
    edge_type = Edge

    @classmethod
    def get_connection_type(cls):
        return cls.connection_type

    @classmethod
    def get_edge_type(cls):
        return cls.edge_type


class Node(BaseNode, Interface):
    '''An object with an ID'''
    id = GlobalIDField()


class MutationInputType(InputObjectType):
    client_mutation_id = StringField(required=True)


class ClientIDMutation(Mutation):
    client_mutation_id = StringField(required=True)

    @classmethod
    def _prepare_class(cls):
        input_type = getattr(cls, 'input_type', None)
        if input_type:
            assert hasattr(cls, 'mutate_and_get_payload'), 'You have to implement mutate_and_get_payload'
            new_input_inner_type = type('{}InnerInput'.format(cls._meta.type_name), (MutationInputType, input_type, ), {})
            items = {
                'input': Field(new_input_inner_type)
            }
            assert issubclass(new_input_inner_type, InputObjectType)
            input_type = type('{}Input'.format(cls._meta.type_name), (ObjectType, ), items)
            setattr(cls, 'input_type', input_type)

    @classmethod
    def mutate(cls, instance, args, info):
        input = args.get('input')
        payload = cls.mutate_and_get_payload(input, info)
        client_mutation_id = input.get('client_mutation_id')
        setattr(payload, 'client_mutation_id', client_mutation_id)
        return payload
