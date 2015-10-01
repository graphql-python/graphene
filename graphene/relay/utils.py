from graphene.relay.types import BaseNode

def is_node(object_type):
	return issubclass(object_type, BaseNode) and not is_node_type(object_type)

def is_node_type(object_type):
	return BaseNode in object_type.__bases__
