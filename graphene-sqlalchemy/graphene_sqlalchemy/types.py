from collections import OrderedDict
import six
from sqlalchemy.inspection import inspect as sqlalchemyinspect
from sqlalchemy.orm.exc import NoResultFound

from graphene import ObjectType
from graphene.relay import is_node
from .converter import (convert_sqlalchemy_column,
                        convert_sqlalchemy_relationship)
from .utils import is_mapped

from graphene.types.objecttype import ObjectTypeMeta
from graphene.types.options import Options
from .registry import Registry, get_global_registry
from graphene.utils.is_base_type import is_base_type
from graphene.types.utils import get_fields_in_type
from .utils import get_query


class SQLAlchemyObjectTypeMeta(ObjectTypeMeta):
    def _construct_fields(cls, all_fields, options):
        only_fields = cls._meta.only_fields
        exclude_fields = cls._meta.exclude_fields
        inspected_model = sqlalchemyinspect(cls._meta.model)

        fields = OrderedDict()

        for name, column in inspected_model.columns.items():
            is_not_in_only = only_fields and name not in only_fields
            is_already_created = name in all_fields
            is_excluded = name in exclude_fields or is_already_created
            if is_not_in_only or is_excluded:
                # We skip this field if we specify only_fields and is not
                # in there. Or when we excldue this field in exclude_fields
                continue
            converted_column = convert_sqlalchemy_column(column, options.registry)
            fields[name] = converted_column

        # Get all the columns for the relationships on the model
        for relationship in inspected_model.relationships:
            is_not_in_only = only_fields and relationship.key not in only_fields
            is_already_created = relationship.key in all_fields
            is_excluded = relationship.key in exclude_fields or is_already_created
            if is_not_in_only or is_excluded:
                # We skip this field if we specify only_fields and is not
                # in there. Or when we excldue this field in exclude_fields
                continue
            converted_relationship = convert_sqlalchemy_relationship(relationship, options.registry)
            name = relationship.key
            fields[name] = converted_relationship

        return fields

    @staticmethod
    def __new__(cls, name, bases, attrs):
        # Also ensure initialization is only performed for subclasses of Model
        # (excluding Model class itself).
        if not is_base_type(bases, SQLAlchemyObjectTypeMeta):
            return type.__new__(cls, name, bases, attrs)

        options = Options(
            attrs.pop('Meta', None),
            name=name,
            description=attrs.pop('__doc__', None),
            model=None,
            fields=None,
            only_fields=(),
            exclude_fields=(),
            id='id',
            interfaces=(),
            registry=None
        )

        if not options.registry:
            options.registry = get_global_registry()
        assert isinstance(options.registry, Registry), (
            'The attribute registry in {}.Meta needs to be an'
            ' instance of Registry, received "{}".'
        ).format(name, options.registry)
        assert is_mapped(options.model), (
            'You need to pass a valid SQLAlchemy Model in '
            '{}.Meta, received "{}".'
        ).format(name, options.model)


        cls = ObjectTypeMeta.__new__(cls, name, bases, dict(attrs, _meta=options))

        options.registry.register(cls)

        options.sqlalchemy_fields = get_fields_in_type(
            ObjectType,
            cls._construct_fields(options.fields, options)
        )
        options.fields.update(options.sqlalchemy_fields)

        return cls


class SQLAlchemyObjectType(six.with_metaclass(SQLAlchemyObjectTypeMeta, ObjectType)):
    @classmethod
    def is_type_of(cls, root, context, info):
        if isinstance(root, cls):
            return True
        if not is_mapped(type(root)):
            raise Exception((
                'Received incompatible instance "{}".'
            ).format(root))
        return type(root) == cls._meta.model

    @classmethod
    def get_node(cls, id, context, info):
        try:
            model = cls._meta.model
            query = get_query(model, context)
            return query.get(id)
        except NoResultFound:
            return None

    def resolve_id(root, args, context, info):
        graphene_type = info.parent_type.graphene_type
        if is_node(graphene_type):
            return root.__mapper__.primary_key_from_instance(root)[0]
        return getattr(root, graphene_type._meta.id, None)
