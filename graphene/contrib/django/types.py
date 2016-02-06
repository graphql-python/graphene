import inspect

import six
from django.db import models

from ...core.classtypes.objecttype import ObjectType, ObjectTypeMeta
from ...relay.types import Connection, Node, NodeMeta
from .converter import convert_django_field_with_choices
from .options import DjangoOptions
from .utils import get_reverse_fields


class DjangoObjectTypeMeta(ObjectTypeMeta):
    options_class = DjangoOptions

    def construct_fields(cls):
        only_fields = cls._meta.only_fields
        reverse_fields = get_reverse_fields(cls._meta.model)
        all_fields = sorted(list(cls._meta.model._meta.fields) +
                            list(cls._meta.model._meta.local_many_to_many))
        all_fields += list(reverse_fields)
        already_created_fields = {f.attname for f in cls._meta.local_fields}

        for field in all_fields:
            is_not_in_only = only_fields and field.name not in only_fields
            is_already_created = field.name in already_created_fields
            is_excluded = field.name in cls._meta.exclude_fields or is_already_created
            if is_not_in_only or is_excluded:
                # We skip this field if we specify only_fields and is not
                # in there. Or when we exclude this field in exclude_fields
                continue
            converted_field = convert_django_field_with_choices(field)
            cls.add_to_class(field.name, converted_field)

    def construct(cls, *args, **kwargs):
        cls = super(DjangoObjectTypeMeta, cls).construct(*args, **kwargs)
        if not cls._meta.abstract:
            if not cls._meta.model:
                raise Exception(
                    'Django ObjectType %s must have a model in the Meta class attr' %
                    cls)
            elif not inspect.isclass(cls._meta.model) or not issubclass(cls._meta.model, models.Model):
                raise Exception('Provided model in %s is not a Django model' % cls)

            cls.construct_fields()
        return cls


class InstanceObjectType(ObjectType):

    class Meta:
        abstract = True

    def __init__(self, _root=None):
        super(InstanceObjectType, self).__init__(_root=_root)
        assert not self._root or isinstance(self._root, self._meta.model), (
            '{} received a non-compatible instance ({}) '
            'when expecting {}'.format(
                self.__class__.__name__,
                self._root.__class__.__name__,
                self._meta.model.__name__
            ))

    @property
    def instance(self):
        return self._root

    @instance.setter
    def instance(self, value):
        self._root = value


class DjangoObjectType(six.with_metaclass(
        DjangoObjectTypeMeta, InstanceObjectType)):

    class Meta:
        abstract = True


class DjangoConnection(Connection):
    pass


class DjangoNodeMeta(DjangoObjectTypeMeta, NodeMeta):
    pass


class NodeInstance(Node, InstanceObjectType):

    class Meta:
        abstract = True


class DjangoNode(six.with_metaclass(
        DjangoNodeMeta, NodeInstance)):

    class Meta:
        abstract = True

    @classmethod
    def get_node(cls, id, info=None):
        try:
            instance = cls._meta.model.objects.get(id=id)
            return cls(instance)
        except cls._meta.model.DoesNotExist:
            return None
