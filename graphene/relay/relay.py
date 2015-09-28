from graphene.relay.nodes import (
	create_node_definitions
)

from graphene.relay.fields import (
	ConnectionField,
)


class Relay(object):
    def __init__(self, schema):
        self.schema = schema
        self.Node, self.NodeField = create_node_definitions(schema=self.schema)
        self.ConnectionField = ConnectionField
