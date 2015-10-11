import inspect
from django.db import models

from graphene.core.options import Options
from graphene.core.types import BaseObjectType
from graphene.relay.utils import is_node

VALID_ATTRS = ('model', 'only_fields', 'exclude_fields')


def is_base(cls):
    from graphene.contrib.django.types import DjangoObjectType
    return DjangoObjectType in cls.__bases__


class DjangoOptions(Options):

    def __init__(self, *args, **kwargs):
        self.model = None
        super(DjangoOptions, self).__init__(*args, **kwargs)
        self.valid_attrs += VALID_ATTRS
        self.only_fields = None
        self.exclude_fields = []

    def contribute_to_class(self, cls, name):
        super(DjangoOptions, self).contribute_to_class(cls, name)
        if not is_node(cls) and not is_base(cls):
            return
        if not self.model:
            raise Exception(
                'Django ObjectType %s must have a model in the Meta class attr' % cls)
        elif not inspect.isclass(self.model) or not issubclass(self.model, models.Model):
            raise Exception('Provided model in %s is not a Django model' % cls)
