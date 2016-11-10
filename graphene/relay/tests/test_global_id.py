from ..node import Node, GlobalID

from ...types import NonNull, ID


class CustomNode(Node):

    class Meta:
        name = 'Node'


def test_global_id_defaults_to_required_and_node():
    gid = GlobalID()
    assert isinstance(gid.type, NonNull)
    assert gid.type.of_type == ID
    assert gid.node == Node


def test_global_id_allows_overriding_of_node_and_required():
    gid = GlobalID(node=CustomNode, required=False)
    assert gid.type == ID
    assert gid.node == CustomNode
