from .types import Node


def is_node(object_type):
    return object_type and issubclass(
        object_type, Node) and not object_type._meta.abstract


def is_node_type(object_type):
    return object_type and issubclass(
        object_type, Node) and object_type._meta.abstract
