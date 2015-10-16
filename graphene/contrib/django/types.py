import six
from django.db import models

from graphene.core.types import ObjectTypeMeta, BaseObjectType
from graphene.contrib.django.options import DjangoOptions
from graphene.contrib.django.converter import convert_django_field

from graphene.relay.types import Node, BaseNode
from graphene.relay.fields import NodeIDField


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
        reverse_fields = get_reverse_fields(cls._meta.model)
        all_fields = sorted(list(cls._meta.model._meta.fields) +
                            list(cls._meta.model._meta.local_many_to_many))
        all_fields += list(reverse_fields)

        for field in all_fields:
            is_not_in_only = only_fields and field.name not in only_fields
            is_excluded = field.name in cls._meta.exclude_fields
            if is_not_in_only or is_excluded:
                # We skip this field if we specify only_fields and is not
                # in there. Or when we excldue this field in exclude_fields
                continue
            converted_field = convert_django_field(field)
            cls.add_to_class(field.name, converted_field)


class DjangoObjectType(six.with_metaclass(DjangoObjectTypeMeta, BaseObjectType)):
    pass


class DjangoInterface(six.with_metaclass(DjangoObjectTypeMeta, BaseObjectType)):
    pass


class DjangoNode(BaseNode, DjangoInterface):
    id = NodeIDField()

    @classmethod
    def get_node(cls, id):
        instance = cls._meta.model.objects.filter(id=id).first()
        return cls(instance)
