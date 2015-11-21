import six
from sqlalchemy.inspection import inspect

from graphene.contrib.sqlalchemy.converter import convert_sqlalchemy_column,
    convert_sqlalchemy_relationship
from graphene.contrib.sqlalchemy.options import SQLAlchemyOptions
from graphene.contrib.sqlalchemy.utils import get_reverse_columns
from graphene.core.types import BaseObjectType, ObjectTypeMeta
from graphene.relay.fields import GlobalIDField
from graphene.relay.types import BaseNode


class SQLAlchemyObjectTypeMeta(ObjectTypeMeta):
    options_cls = SQLAlchemyOptions

    def is_interface(cls, parents):
        return SQLAlchemyInterface in parents

    def add_extra_fields(cls):
        if not cls._meta.table:
            return
        inspected_table = inspect(cls._meta.table)
        # Get all the columns for the relationships on the table
        for relationship in inspected_table.relationships:
            converted_relationship = convert_sqlalchemy_relationship(relationship)
            cls.add_to_class(relationship.key, converted_relationship)
        for column in inspected_table.columns:
            converted_column = convert_sqlalchemy_column(column)
            cls.add_to_class(column.name, converted_column)


class InstanceObjectType(BaseObjectType):

    def __init__(self, instance=None):
        self.instance = instance
        super(InstanceObjectType, self).__init__()

    def __getattr__(self, attr):
        return getattr(self.instance, attr)


class SQLAlchemyObjectType(six.with_metaclass(SQLAlchemyObjectTypeMeta, InstanceObjectType)):
    pass


class SQLAlchemyInterface(six.with_metaclass(SQLAlchemyObjectTypeMeta, InstanceObjectType)):
    pass


class SQLAlchemyNode(BaseNode, SQLAlchemyInterface):
    id = GlobalIDField()

    @classmethod
    def get_node(cls, id):
        instance = cls._meta.table.objects.filter(id=id).first()
        return cls(instance)
