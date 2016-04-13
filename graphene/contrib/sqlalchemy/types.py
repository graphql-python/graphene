import inspect

import six
from sqlalchemy.inspection import inspect as sqlalchemyinspect
from sqlalchemy.orm.exc import NoResultFound

from ...core.classtypes.objecttype import ObjectType, ObjectTypeMeta
from ...relay.types import Connection, Node, NodeMeta
from .converter import (convert_sqlalchemy_column,
                        convert_sqlalchemy_relationship)
from .options import SQLAlchemyOptions
from .utils import get_query, is_mapped


class SQLAlchemyObjectTypeMeta(ObjectTypeMeta):
    options_class = SQLAlchemyOptions

    def construct_fields(cls):
        only_fields = cls._meta.only_fields
        exclude_fields = cls._meta.exclude_fields
        already_created_fields = {f.attname for f in cls._meta.local_fields}
        inspected_model = sqlalchemyinspect(cls._meta.model)

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

    def construct(cls, *args, **kwargs):
        cls = super(SQLAlchemyObjectTypeMeta, cls).construct(*args, **kwargs)
        if not cls._meta.abstract:
            if not cls._meta.model:
                raise Exception(
                    'SQLAlchemy ObjectType %s must have a model in the Meta class attr' %
                    cls)
            elif not inspect.isclass(cls._meta.model) or not is_mapped(cls._meta.model):
                raise Exception('Provided model in %s is not a SQLAlchemy model' % cls)

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


class SQLAlchemyObjectType(six.with_metaclass(
        SQLAlchemyObjectTypeMeta, InstanceObjectType)):

    class Meta:
        abstract = True


class SQLAlchemyConnection(Connection):
    pass


class SQLAlchemyNodeMeta(SQLAlchemyObjectTypeMeta, NodeMeta):
    pass


class NodeInstance(Node, InstanceObjectType):

    class Meta:
        abstract = True


class SQLAlchemyNode(six.with_metaclass(
        SQLAlchemyNodeMeta, NodeInstance)):

    class Meta:
        abstract = True

    def to_global_id(self):
        id_ = getattr(self.instance, self._meta.identifier)
        return self.global_id(id_)

    @classmethod
    def get_node(cls, id, info=None):
        try:
            model = cls._meta.model
            identifier = cls._meta.identifier
            query = get_query(model, info)
            instance = query.filter(getattr(model, identifier) == id).one()
            return cls(instance)
        except NoResultFound:
            return None
