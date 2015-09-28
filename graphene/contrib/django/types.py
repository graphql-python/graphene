import six

from graphene.core.types import ObjectTypeMeta, ObjectType
from graphene.contrib.django.options import DjangoOptions
from graphene.contrib.django.converter import convert_django_field

from graphene.relay import Node

class DjangoObjectTypeMeta(ObjectTypeMeta):
    options_cls = DjangoOptions
    def add_extra_fields(cls):
        if not cls._meta.model:
            return

        only_fields = cls._meta.only_fields
        # print cls._meta.model._meta._get_fields(forward=False, reverse=True, include_hidden=True)
        for field in cls._meta.model._meta.fields:
            if only_fields and field.name not in only_fields:
                continue
            converted_field = convert_django_field(field)
            cls.add_to_class(field.name, converted_field)


class DjangoObjectType(six.with_metaclass(DjangoObjectTypeMeta, ObjectType)):
    class Meta:
        proxy = True


class DjangoNode(six.with_metaclass(DjangoObjectTypeMeta, Node)):
    class Meta:
        proxy = True
