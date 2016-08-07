from .definitions import (
    GrapheneInterfaceType,
    GrapheneObjectType,
    GrapheneScalarType,
    GrapheneEnumType,
    GrapheneInputObjectType
)
from .utils import values_from_enum


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


def generate_scalar(scalar):
    return GrapheneScalarType(
        graphene_type=scalar,
        name=scalar._meta.name or scalar.__name__,
        description=scalar._meta.description or scalar.__doc__,

        serialize=getattr(scalar, 'serialize', None),
        parse_value=getattr(scalar, 'parse_value', None),
        parse_literal=getattr(scalar, 'parse_literal', None),
    )


def generate_enum(enum):
    return GrapheneEnumType(
        graphene_type=enum,
        values=values_from_enum(enum._meta.enum),
        name=enum._meta.name or enum.__name__,
        description=enum._meta.description or enum.__doc__,
    )


def generate_inputobjecttype(inputobjecttype):
    return GrapheneInputObjectType(
        graphene_type=inputobjecttype,
        name=inputobjecttype._meta.name or inputobjecttype.__name__,
        description=inputobjecttype._meta.description or inputobjecttype.__doc__,
        fields=inputobjecttype._meta.get_fields,
    )
