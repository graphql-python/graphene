import inspect

from sqlalchemy import Table

from graphene.core.options import Options
from graphene.relay.types import Node
from graphene.relay.utils import is_node

VALID_ATTRS = ('table', 'only_columns', 'exclude_columns')


def is_base(cls):
    from graphene.contrib.SQLAlchemy.types import SQLAlchemyObjectType
    return SQLAlchemyObjectType in cls.__bases__


class SQLAlchemyOptions(Options):

    def __init__(self, *args, **kwargs):
        self.table = None
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
        if not self.table:
            raise Exception(
                'SQLAlchemy ObjectType %s must have a table in the Meta class attr' % cls)
        elif not inspect.isclass(self.table) or not issubclass(self.table, Table):
            raise Exception('Provided table in %s is not a SQLAlchemy table' % cls)
