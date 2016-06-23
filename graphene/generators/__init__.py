from .definitions import GrapheneInterfaceType, GrapheneObjectType


def generate_interface(interface):
    return GrapheneInterfaceType(
        graphene_type=interface,
        name=interface._meta.name or interface.__name__,
        resolve_type=interface.resolve_type,
        description=interface._meta.description or interface.__doc__,
        fields=interface._meta.get_fields,
    )


def generate_objecttype(objecttype):
    return GrapheneObjectType(
        graphene_type=objecttype,
        name=objecttype._meta.name or objecttype.__name__,
        description=objecttype._meta.description or objecttype.__doc__,
        fields=objecttype._meta.get_fields,
        is_type_of=objecttype.is_type_of,
        interfaces=objecttype._meta.get_interfaces
    )
