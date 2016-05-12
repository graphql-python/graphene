from functools import partial

import six
from graphql.type import GraphQLInterfaceType

from .base import FieldsClassTypeMeta
from .objecttype import ObjectType, ObjectTypeMeta


class InterfaceMeta(ObjectTypeMeta):

    def construct(cls, bases, attrs):
        if cls._meta.abstract or Interface in bases:
            # Return Interface type
            cls = FieldsClassTypeMeta.construct(cls, bases, attrs)
            setattr(cls._meta, 'interface', True)
            return cls
        else:
            # Return ObjectType class with all the inherited interfaces
            cls = super(InterfaceMeta, cls).construct(bases, attrs)
            for interface in bases:
                is_interface = issubclass(interface, Interface) and getattr(interface._meta, 'interface', False)
                if not is_interface:
                    continue
                cls._meta.interfaces.append(interface)
            return cls


class Interface(six.with_metaclass(InterfaceMeta, ObjectType)):

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        if self._meta.interface:
            raise Exception("An interface cannot be initialized")
        return super(Interface, self).__init__(*args, **kwargs)

    @classmethod
    def _resolve_type(cls, schema, instance, *args):
        return schema.T(instance.__class__)

    @classmethod
    def internal_type(cls, schema):
        if not cls._meta.interface:
            return super(Interface, cls).internal_type(schema)

        return GraphQLInterfaceType(
            cls._meta.type_name,
            description=cls._meta.description,
            resolve_type=partial(cls._resolve_type, schema),
            fields=partial(cls.fields_internal_types, schema)
        )
