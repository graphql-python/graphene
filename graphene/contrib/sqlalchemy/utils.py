from sqlalchemy.ext.declarative.api import DeclarativeMeta


# from sqlalchemy.orm.base import object_mapper
# from sqlalchemy.orm.exc import UnmappedInstanceError


def get_type_for_model(schema, model):
    schema = schema
    types = schema.types.values()
    for _type in types:
        type_model = hasattr(_type, '_meta') and getattr(
            _type._meta, 'model', None)
        if model == type_model:
            return _type


def is_mapped(obj):
    return isinstance(obj, DeclarativeMeta)
    # try:
    #     object_mapper(obj)
    # except UnmappedInstanceError:
    #     return False
    # return True
