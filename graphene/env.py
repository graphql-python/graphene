from graphene.core.schema import Schema

_global_schema = None

def get_global_schema():
	global _global_schema
	if not _global_schema:
		_global_schema = Schema(name='Global Schema')
	return _global_schema
