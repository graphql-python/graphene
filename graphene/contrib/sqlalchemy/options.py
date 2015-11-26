import inspect

from sqlalchemy.ext.declarative.api import DeclarativeMeta

from ...core.options import Options
from ...relay.types import Node
from ...relay.utils import is_node

VALID_ATTRS = ('model', 'only_fields', 'exclude_fields')


def is_base(cls):
    from graphene.contrib.sqlalchemy.types import SQLAlchemyObjectType
    return SQLAlchemyObjectType in cls.__bases__


class SQLAlchemyOptions(Options):

    def __init__(self, *args, **kwargs):
        self.model = None
        super(SQLAlchemyOptions, self).__init__(*args, **kwargs)
        self.valid_attrs += VALID_ATTRS
        self.only_fields = None
        self.exclude_fields = []

    def contribute_to_class(self, cls, name):
        super(SQLAlchemyOptions, self).contribute_to_class(cls, name)
        if is_node(cls):
            self.exclude_fields = list(self.exclude_fields)
            self.interfaces.append(Node)
        if not is_node(cls) and not is_base(cls):
            return
        if not self.model:
            raise Exception(
                'SQLAlchemy ObjectType %s must have a model in the Meta class attr' % cls)
        elif not inspect.isclass(self.model) or not isinstance(self.model, DeclarativeMeta):
            raise Exception('Provided model in %s is not a SQLAlchemy model' % cls)
