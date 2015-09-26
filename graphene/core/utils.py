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
            object_type = get_registered_object_type(field_type, object_type)
            field_type = object_type._meta.type
    return field_type


def get_registered_object_type(name, object_type=None):
    app_label = None
    object_type_name = name

    if '.' in name:
        app_label, object_type_name = name.rsplit('.', 1)
    elif object_type:
        app_label = object_type._meta.app_label

    # Filter all registered object types which have the same name
    ots = [ot for ot in registered_object_types if ot._meta.type_name == object_type_name]
    # If the list have more than one object type with the name, filter by
    # the app_label
    if len(ots)>1 and app_label:
        ots = [ot for ot in ots if ot._meta.app_label == app_label]

    if len(ots)>1:
        raise Exception('Multiple ObjectTypes returned with the name %s' % name)
    if not ots:
        raise Exception('No ObjectType found with name %s' % name)

    return ots[0]


@signals.class_prepared.connect
def object_type_created(sender):
    registered_object_types.append(sender)
