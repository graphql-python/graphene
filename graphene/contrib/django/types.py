import six
from django.db import models

from graphene.core.types import ObjectTypeMeta, BaseObjectType
from graphene.contrib.django.options import DjangoOptions
from graphene.contrib.django.converter import convert_django_field

from graphene.relay.types import Node, BaseNode


def get_reverse_fields(model):
    for name, attr in model.__dict__.items():
        related = getattr(attr, 'related', None)
        if isinstance(related, models.ManyToOneRel):
            yield related


class DjangoObjectTypeMeta(ObjectTypeMeta):
    options_cls = DjangoOptions

    def is_interface(cls, parents):
        return DjangoInterface in parents

    def add_extra_fields(cls):
        if not cls._meta.model:
            return
        only_fields = cls._meta.only_fields
        reverse_fields = tuple(get_reverse_fields(cls._meta.model))
        for field in cls._meta.model._meta.fields + reverse_fields:
            if only_fields and field.name not in only_fields:
                continue
            converted_field = convert_django_field(field, cls)
            cls.add_to_class(field.name, converted_field)


class DjangoObjectType(six.with_metaclass(DjangoObjectTypeMeta, BaseObjectType)):
    pass


class DjangoInterface(six.with_metaclass(DjangoObjectTypeMeta, BaseObjectType)):
    pass


class DjangoNode(BaseNode, DjangoInterface):
    pass
