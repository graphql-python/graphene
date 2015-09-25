import inspect

from graphene.core.types import ObjectType
from graphene import signals

registered_object_types = []


def get_object_type(field_type, object_type=None):
    _is_class = inspect.isclass(field_type)
    if _is_class and issubclass(field_type, ObjectType):
        field_type = field_type._meta.type
    elif isinstance(field_type, basestring):
        if field_type == 'self':
            field_type = object_type._meta.type
        else:
            object_type = get_registered_object_type(field_type)
            field_type = object_type._meta.type
    return field_type


def get_registered_object_type(name):
    for object_type in registered_object_types:
        if object_type._meta.type_name == name:
            return object_type
    return None

@signals.class_prepared.connect
def object_type_created(sender):
    registered_object_types.append(sender)
