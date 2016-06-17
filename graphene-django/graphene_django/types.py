import inspect

import six
from django.db import models

from graphene import Field, Interface
from graphene.types.objecttype import ObjectType, ObjectTypeMeta, attrs_without_fields, GrapheneObjectType, get_interfaces
from graphene.types.interface import InterfaceTypeMeta
from graphene.relay import Connection, Node
from graphene.relay.node import NodeMeta
from .converter import convert_django_field_with_choices, Registry
from graphene.types.options import Options
from graphene import String
from .utils import get_model_fields
from graphene.utils.is_base_type import is_base_type

from graphene.utils.copy_fields import copy_fields
from graphene.utils.get_fields import get_fields
from graphene.utils.is_base_type import is_base_type


class DjangoObjectTypeMeta(ObjectTypeMeta):
    def __new__(cls, name, bases, attrs):
        # super_new = super(DjangoObjectTypeMeta, cls).__new__
        super_new = type.__new__

        # Also ensure initialization is only performed for subclasses of Model
        # (excluding Model class itself).
        if not is_base_type(bases, DjangoObjectTypeMeta):
            return super_new(cls, name, bases, attrs)

        options = Options(
            attrs.pop('Meta', None),
            name=None,
            description=None,
            model=None,
            fields=(),
            exclude=(),
            interfaces=(),
        )
        assert options.model, 'You need to pass a valid Django Model in {}.Meta'.format(name)
        get_model_fields(options.model)

        interfaces = tuple(options.interfaces)
        fields = get_fields(ObjectType, attrs, bases, interfaces)
        attrs = attrs_without_fields(attrs, fields)
        cls = super_new(cls, name, bases, dict(attrs, _meta=options))

        fields = copy_fields(Field, fields, parent=cls)
        base_interfaces = tuple(b for b in bases if issubclass(b, Interface))
        options.graphql_type = GrapheneObjectType(
            graphene_type=cls,
            name=options.name or cls.__name__,
            description=options.description or cls.__doc__,
            fields=fields,
            interfaces=tuple(get_interfaces(interfaces + base_interfaces))
        )

        # for field in all_fields:
        #     is_not_in_only = only_fields and field.name not in only_fields
        #     is_already_created = field.name in already_created_fields
        #     is_excluded = field.name in cls._meta.exclude_fields or is_already_created
        #     if is_not_in_only or is_excluded:
        #         # We skip this field if we specify only_fields and is not
        #         # in there. Or when we exclude this field in exclude_fields
        #         continue
        #         converted_field = convert_django_field_with_choices(field)
        return cls


class DjangoObjectType(six.with_metaclass(DjangoObjectTypeMeta, ObjectType)):
    _registry = None

    @classmethod
    def get_registry(cls):
        if not DjangoObjectType._registry:
            DjangoObjectType._registry = Registry()
        return DjangoObjectType._registry


class DjangoNodeMeta(DjangoObjectTypeMeta, NodeMeta):
    pass


class DjangoNode(six.with_metaclass(DjangoNodeMeta, Node)):
    @classmethod
    def get_node(cls, id, context, info):
        try:
            instance = cls._meta.model.objects.get(id=id)
            return cls(instance)
        except cls._meta.model.DoesNotExist:
            return None
