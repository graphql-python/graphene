from ...types import ObjectType, Field, Schema, String, NonNull
from ...relay import Connection, ConnectionField


def _get_query(_edge_required=False, _node_required=False):
    class UserPhoto(ObjectType):
        uri = String()

    class UserPhotosConnection(Connection):
        class Meta:
            node = UserPhoto

        class Edge:
            class Meta:
                required = _edge_required
                node_required = _node_required

    class User(ObjectType):
        name = String(required=True)
        user_photos = ConnectionField(UserPhotosConnection)

        def resolve_user_photos(self, info):
            return [UserPhoto(uri="user-1-uri")]

    class Query(ObjectType):
        user = Field(User)

        def resolve_user(self, info):
            return User(name="user-1")

    return Query


def _get_edge_field(schema):
    return schema.query.user._type.user_photos._type._meta.fields[
        "edges"
    ]._type.of_type.of_type


def test_required_nonnull_edge_only():
    """
    Test that elements in the edge are required
    """
    schema = Schema(query=_get_query(True))

    # Edge
    assert isinstance(
        _get_edge_field(schema),
        NonNull,
    )
    # Node
    assert not isinstance(
        _get_edge_field(schema).of_type.node._type,
        NonNull,
    )


def test_required_nonnull_node_only():
    """
    Test that elements in the edge are required
    """
    schema = Schema(query=_get_query(False, True))

    # Edge
    assert not isinstance(
        _get_edge_field(schema),
        NonNull,
    )
    # Node
    assert isinstance(
        _get_edge_field(schema).node._type,
        NonNull,
    )


def test_support_null_nodes():
    """
    Test that elements in the edge are required
    """
    schema = Schema(query=_get_query())

    assert not isinstance(
        _get_edge_field(schema),
        NonNull,
    )

    assert not isinstance(
        _get_edge_field(schema).node._type,
        NonNull,
    )
