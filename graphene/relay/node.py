from graphql_relay import from_global_id, to_global_id
from ..types import Interface, ID, Field


class Node(Interface):
    '''An object with an ID'''

    id = ID(required=True, description='The ID of the object.')

    @classmethod
    def resolve_id(cls, root, args, context, info):
        type_name = root._meta.name  # info.parent_type.name
        return cls.to_global_id(type_name, getattr(root, 'id', None))

    @classmethod
    def Field(cls):
        def resolve_node(root, args, context, info):
            return cls.get_node_from_global_id(args.get('id'), context, info)

        return Field(
            cls,
            description='The ID of the object',
            id=ID(required=True),
            resolver=resolve_node
        )

    @classmethod
    def get_node_from_global_id(cls, global_id, context, info):
        try:
            _type, _id = cls.from_global_id(global_id)
            graphene_type = info.schema.get_type(_type).graphene_type
            # We make sure the ObjectType implements the "Node" interface
            assert cls in graphene_type._meta.interfaces
        except:
            return None
        return graphene_type.get_node(_id, context, info)

    @classmethod
    def from_global_id(cls, global_id):
        return from_global_id(global_id)

    @classmethod
    def to_global_id(cls, type, id):
        return to_global_id(type, id)

    @classmethod
    def implements(cls, objecttype):
        require_get_node = Node in objecttype._meta.interfaces
        # get_connection = getattr(objecttype, 'get_connection', None)
        # if not get_connection:
        #     get_connection = partial(get_default_connection, objecttype)

        # objecttype.Connection = get_connection()
        if require_get_node:
            assert hasattr(
                objecttype, 'get_node'), '{}.get_node method is required by the Node interface.'.format(
                objecttype.__name__)
