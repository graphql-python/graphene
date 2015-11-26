import six
from sqlalchemy.inspection import inspect

from ...core.types import BaseObjectType, ObjectTypeMeta
from ...relay.fields import GlobalIDField
from ...relay.types import BaseNode
from .converter import convert_sqlalchemy_column, convert_sqlalchemy_relationship
from .options import SQLAlchemyOptions


class SQLAlchemyObjectTypeMeta(ObjectTypeMeta):
    options_cls = SQLAlchemyOptions

    def is_interface(cls, parents):
        return SQLAlchemyInterface in parents

    def add_extra_fields(cls):
        if not cls._meta.model:
            return
        only_fields = cls._meta.only_fields
        exclude_fields = cls._meta.exclude_fields
        already_created_fields = {f.attname for f in cls._meta.local_fields}
        inspected_model = inspect(cls._meta.model)

        # Get all the columns for the relationships on the model
        for relationship in inspected_model.relationships:
            is_not_in_only = only_fields and relationship.key not in only_fields
            is_already_created = relationship.key in already_created_fields
            is_excluded = relationship.key in exclude_fields or is_already_created
            if is_not_in_only or is_excluded:
                # We skip this field if we specify only_fields and is not
                # in there. Or when we excldue this field in exclude_fields
                continue
            converted_relationship = convert_sqlalchemy_relationship(relationship)
            cls.add_to_class(relationship.key, converted_relationship)

        for column in inspected_model.columns:
            is_not_in_only = only_fields and column.name not in only_fields
            is_already_created = column.name in already_created_fields
            is_excluded = column.name in exclude_fields or is_already_created
            if is_not_in_only or is_excluded:
                # We skip this field if we specify only_fields and is not
                # in there. Or when we excldue this field in exclude_fields
                continue
            converted_column = convert_sqlalchemy_column(column)
            cls.add_to_class(column.name, converted_column)


class InstanceObjectType(BaseObjectType):

    def __init__(self, _root=None):
        if _root:
            assert isinstance(_root, self._meta.model), (
                '{} received a non-compatible instance ({}) '
                'when expecting {}'.format(
                    self.__class__.__name__,
                    _root.__class__.__name__,
                    self._meta.model.__name__
                ))
        super(InstanceObjectType, self).__init__(_root=_root)

    @property
    def instance(self):
        return self._root

    @instance.setter
    def instance(self, value):
        self._root = value

    def __getattr__(self, attr):
        return getattr(self._root, attr)


class SQLAlchemyObjectType(six.with_metaclass(SQLAlchemyObjectTypeMeta, InstanceObjectType)):
    pass


class SQLAlchemyInterface(six.with_metaclass(SQLAlchemyObjectTypeMeta, InstanceObjectType)):
    pass


class SQLAlchemyNode(BaseNode, SQLAlchemyInterface):
    id = GlobalIDField()

    @classmethod
    def get_node(cls, id, info=None):
        try:
            instance = cls._meta.model.filter(id=id).one()
            return cls(instance)
        except cls._meta.model.DoesNotExist:
            return None
