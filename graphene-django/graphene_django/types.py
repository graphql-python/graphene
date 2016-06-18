import inspect
from collections import OrderedDict
from functools import partial

import six
from django.db import models

from graphene import Field, Interface
from graphene.types.objecttype import ObjectType, ObjectTypeMeta, attrs_without_fields, GrapheneObjectType, get_interfaces
from graphene.types.interface import InterfaceTypeMeta
from graphene.relay import Connection, Node
from graphene.relay.node import NodeMeta
from .converter import convert_django_field_with_choices
from graphene.types.options import Options
from .utils import get_model_fields
from .registry import Registry, get_global_registry
from graphene.utils.is_base_type import is_base_type
from graphene.utils.copy_fields import copy_fields
from graphene.utils.get_fields import get_fields
from graphene.utils.as_field import as_field


class DjangoObjectTypeMeta(ObjectTypeMeta):
    def _construct_fields(cls, fields, options):
        _model_fields = get_model_fields(options.model)

        for field in _model_fields:
            name = field.name
            is_not_in_only = options.fields and name not in options.fields
            is_already_created = name in fields
            is_excluded = field.name in options.exclude or is_already_created
            if is_not_in_only or is_excluded:
                # We skip this field if we specify only_fields and is not
                # in there. Or when we exclude this field in exclude_fields
                continue
            converted = convert_django_field_with_choices(field, options.registry)
            if not converted:
                continue
            fields[name] = as_field(converted)

        fields = copy_fields(Field, fields, parent=cls)

        return fields

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
            registry=None
        )
        if not options.registry:
            options.registry = get_global_registry()
        assert isinstance(options.registry, Registry), 'The attribute registry in {}.Meta needs to be an instance of Registry.'.format(name)
        assert options.model, 'You need to pass a valid Django Model in {}.Meta'.format(name)

        interfaces = tuple(options.interfaces)
        fields = get_fields(ObjectType, attrs, bases, interfaces)
        attrs = attrs_without_fields(attrs, fields)
        cls = super_new(cls, name, bases, dict(attrs, _meta=options))

        base_interfaces = tuple(b for b in bases if issubclass(b, Interface))
        options.graphql_type = GrapheneObjectType(
            graphene_type=cls,
            name=options.name or cls.__name__,
            description=options.description or cls.__doc__,
            fields=partial(cls._construct_fields, fields, options),
            interfaces=tuple(get_interfaces(interfaces + base_interfaces))
        )

        if issubclass(cls,  DjangoObjectType):
            options.registry.register(cls)

        return cls


class DjangoObjectType(six.with_metaclass(DjangoObjectTypeMeta, ObjectType)):
    pass


class DjangoNodeMeta(DjangoObjectTypeMeta, NodeMeta):
    pass


class DjangoNode(six.with_metaclass(DjangoNodeMeta, Node)):
    @classmethod
    def get_node(cls, id, context, info):
        try:
            return cls._meta.model.objects.get(id=id)
        except cls._meta.model.DoesNotExist:
            return None
