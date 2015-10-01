import inspect
from django.db import models

from graphene.core.options import Options

VALID_ATTRS = ('model', 'only_fields')

from graphene.relay.types import Node, BaseNode

class DjangoOptions(Options):
    def __init__(self, *args, **kwargs):
        self.model = None
        super(DjangoOptions, self).__init__(*args, **kwargs)
        self.valid_attrs += VALID_ATTRS
        self.only_fields = None

    def contribute_to_class(self, cls, name):
        super(DjangoOptions, self).contribute_to_class(cls, name)
        if cls.__name__ == 'DjangoNode':
            return
        if not self.model:
            raise Exception('Django ObjectType %s must have a model in the Meta class attr' % cls)
        elif not inspect.isclass(self.model) or not issubclass(self.model, models.Model):
            raise Exception('Provided model in %s is not a Django model' % cls)
