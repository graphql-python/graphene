def get_relay(schema):
    return getattr(schema, 'relay', None)


def setup(schema):
	from graphene.relay.relay import Relay
	if not hasattr(schema, 'relay'):
		return setattr(schema, 'relay', Relay(schema))
	return schema
