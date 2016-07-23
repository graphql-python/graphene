import six
from sqlalchemy.inspection import inspect as sqlalchemyinspect
from sqlalchemy.orm.exc import NoResultFound

from graphene import ObjectType
from graphene.relay import Node
from .converter import (convert_sqlalchemy_column,
                        convert_sqlalchemy_relationship)
from .utils import is_mapped

from functools import partial


from graphene import Field, Interface
from graphene.types.options import Options
from graphene.types.objecttype import attrs_without_fields, get_interfaces

from .registry import Registry, get_global_registry
from .utils import get_query
from graphene.utils.is_base_type import is_base_type
from graphene.utils.copy_fields import copy_fields
from graphene.utils.get_graphql_type import get_graphql_type
from graphene.utils.get_fields import get_fields
from graphene.utils.as_field import as_field
from graphene.generators import generate_objecttype


class SQLAlchemyObjectTypeMeta(type(ObjectType)):
    def _construct_fields(cls, fields, options):
        only_fields = cls._meta.only
        exclude_fields = cls._meta.exclude
        inspected_model = sqlalchemyinspect(cls._meta.model)

        # Get all the columns for the relationships on the model
        for relationship in inspected_model.relationships:
            is_not_in_only = only_fields and relationship.key not in only_fields
            is_already_created = relationship.key in fields
            is_excluded = relationship.key in exclude_fields or is_already_created
            if is_not_in_only or is_excluded:
                # We skip this field if we specify only_fields and is not
                # in there. Or when we excldue this field in exclude_fields
                continue
            converted_relationship = convert_sqlalchemy_relationship(relationship, options.registry)
            if not converted_relationship:
                continue
            name = relationship.key
            fields[name] = as_field(converted_relationship)

        for name, column in inspected_model.columns.items():
            is_not_in_only = only_fields and name not in only_fields
            is_already_created = name in fields
            is_excluded = name in exclude_fields or is_already_created
            if is_not_in_only or is_excluded:
                # We skip this field if we specify only_fields and is not
                # in there. Or when we excldue this field in exclude_fields
                continue
            converted_column = convert_sqlalchemy_column(column, options.registry)
            if not converted_column:
                continue
            fields[name] = as_field(converted_column)

        fields = copy_fields(Field, fields, parent=cls)

        return fields

    @staticmethod
    def _create_objecttype(cls, name, bases, attrs):
        # super_new = super(SQLAlchemyObjectTypeMeta, cls).__new__
        super_new = type.__new__

        # Also ensure initialization is only performed for subclasses of Model
        # (excluding Model class itself).
        if not is_base_type(bases, SQLAlchemyObjectTypeMeta):
            return super_new(cls, name, bases, attrs)

        options = Options(
            attrs.pop('Meta', None),
            name=None,
            description=None,
            model=None,
            fields=(),
            exclude=(),
            only=(),
            interfaces=(),
            registry=None
        )

        if not options.registry:
            options.registry = get_global_registry()
        assert isinstance(options.registry, Registry), 'The attribute registry in {}.Meta needs to be an instance of Registry, received "{}".'.format(name, options.registry)
        assert is_mapped(options.model), 'You need to pass a valid SQLAlchemy Model in {}.Meta, received "{}".'.format(name, options.model)

        interfaces = tuple(options.interfaces)
        fields = get_fields(ObjectType, attrs, bases, interfaces)
        attrs = attrs_without_fields(attrs, fields)
        cls = super_new(cls, name, bases, dict(attrs, _meta=options))

        base_interfaces = tuple(b for b in bases if issubclass(b, Interface))
        options.get_fields = partial(cls._construct_fields, fields, options)
        options.get_interfaces = tuple(get_interfaces(interfaces + base_interfaces))

        options.graphql_type = generate_objecttype(cls)

        if issubclass(cls, SQLAlchemyObjectType):
            options.registry.register(cls)

        return cls


class SQLAlchemyObjectType(six.with_metaclass(SQLAlchemyObjectTypeMeta, ObjectType)):
    is_type_of = None


class SQLAlchemyNodeMeta(SQLAlchemyObjectTypeMeta, type(Node)):

    @staticmethod
    def _get_interface_options(meta):
        return Options(
            meta,
            name=None,
            description=None,
            model=None,
            graphql_type=None,
            registry=False
        )

    @staticmethod
    def _create_interface(cls, name, bases, attrs):
        cls = super(SQLAlchemyNodeMeta, cls)._create_interface(cls, name, bases, attrs)
        if not cls._meta.registry:
            cls._meta.registry = get_global_registry()
        assert isinstance(cls._meta.registry, Registry), 'The attribute registry in {}.Meta needs to be an instance of Registry.'.format(name)
        return cls


class SQLAlchemyNode(six.with_metaclass(SQLAlchemyNodeMeta, Node)):
    @classmethod
    def get_node(cls, id, context, info):
        try:
            model = cls._meta.model
            query = get_query(model, context)
            return query.get(id)
        except NoResultFound:
            return None

    @classmethod
    def resolve_id(cls, root, args, context, info):
        return root.__mapper__.primary_key_from_instance(root)[0]

    @classmethod
    def resolve_type(cls, type_instance, context, info):
        # We get the model from the _meta in the SQLAlchemy class/instance
        model = type(type_instance)
        graphene_type = cls._meta.registry.get_type_for_model(model)
        if graphene_type:
            return get_graphql_type(graphene_type)

        raise Exception("Type not found for model \"{}\"".format(model))
