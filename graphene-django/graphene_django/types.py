from collections import OrderedDict

import six

from graphene import ObjectType
from graphene.types.objecttype import ObjectTypeMeta
from .converter import convert_django_field_with_choices
from graphene.types.options import Options
from .utils import get_model_fields, is_valid_django_model, DJANGO_FILTER_INSTALLED
from .registry import Registry, get_global_registry
from graphene.utils.is_base_type import is_base_type
from graphene.types.utils import get_fields_in_type, merge


def construct_fields(options):
    _model_fields = get_model_fields(options.model)
    only_fields = options.only_fields
    exclude_fields = options.exclude_fields

    fields = OrderedDict()
    for field in _model_fields:
        name = field.name
        is_not_in_only = only_fields and name not in options.only_fields
        is_already_created = name in options.fields
        is_excluded = name in exclude_fields or is_already_created
        if is_not_in_only or is_excluded:
            # We skip this field if we specify only_fields and is not
            # in there. Or when we exclude this field in exclude_fields
            continue
        converted = convert_django_field_with_choices(field, options.registry)
        if not converted:
            continue
        fields[name] = converted

    return fields


class DjangoObjectTypeMeta(ObjectTypeMeta):

    @staticmethod
    def __new__(cls, name, bases, attrs):
        # Also ensure initialization is only performed for subclasses of
        # DjangoObjectType
        if not is_base_type(bases, DjangoObjectTypeMeta):
            return type.__new__(cls, name, bases, attrs)

        defaults = dict(
            name=name,
            description=attrs.pop('__doc__', None),
            model=None,
            local_fields=None,
            only_fields=(),
            exclude_fields=(),
            interfaces=(),
            registry=None
        )
        if DJANGO_FILTER_INSTALLED:
            # In case Django filter is available, then
            # we allow more attributes in Meta
            defaults.update(
                filter_fields=(),
                filter_order_by=(),
            )

        options = Options(
            attrs.pop('Meta', None),
            **defaults
        )
        if not options.registry:
            options.registry = get_global_registry()
        assert isinstance(options.registry, Registry), (
            'The attribute registry in {}.Meta needs to be an instance of '
            'Registry, received "{}".'
        ).format(name, options.registry)
        assert is_valid_django_model(options.model), (
            'You need to pass a valid Django Model in {}.Meta, received "{}".'
        ).format(name, options.model)

        cls = ObjectTypeMeta.__new__(cls, name, bases, dict(attrs, _meta=options))

        options.registry.register(cls)

        options.django_fields = get_fields_in_type(
            ObjectType,
            construct_fields(options)
        )
        options.fields = merge(
            options.interface_fields,
            options.django_fields,
            options.base_fields,
            options.local_fields
        )

        return cls


class DjangoObjectType(six.with_metaclass(DjangoObjectTypeMeta, ObjectType)):
    @classmethod
    def is_type_of(cls, root, context, info):
        if isinstance(root, cls):
            return True
        if not is_valid_django_model(type(root)):
            raise Exception((
                'Received incompatible instance "{}".'
            ).format(root))
        model = root._meta.model
        return model == cls._meta.model

    @classmethod
    def get_node(cls, id, context, info):
        try:
            return cls._meta.model.objects.get(id=id)
        except cls._meta.model.DoesNotExist:
            return None
