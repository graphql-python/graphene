from django.db import models
from django.utils.encoding import force_text

from graphene import Enum, List, ID, Boolean, Float, Int, String, NonNull, Field, Dynamic
from graphene.types.json import JSONString
from graphene.types.datetime import DateTime
from graphene.utils.str_converters import to_const
from graphene.relay import is_node

from .compat import (ArrayField, HStoreField, JSONField, RangeField,
                     RelatedObject, UUIDField)
from .utils import get_related_model, import_single_dispatch
from .fields import get_connection_field

singledispatch = import_single_dispatch()


def convert_choice_name(name):
    return to_const(force_text(name))


def get_choices(choices):
    for value, help_text in choices:
        if isinstance(help_text, (tuple, list)):
            for choice in get_choices(help_text):
                yield choice
        else:
            name = convert_choice_name(help_text)
            description = help_text
            yield name, value, description


def convert_django_field_with_choices(field, registry=None):
    choices = getattr(field, 'choices', None)
    if choices:
        meta = field.model._meta
        name = '{}{}'.format(meta.object_name, field.name.capitalize())
        choices = list(get_choices(choices))
        named_choices = [(c[0], c[1]) for c in choices]
        named_choices_descriptions = {c[0]: c[2] for c in choices}

        class EnumWithDescriptionsType(object):
            @property
            def description(self):
                return named_choices_descriptions[self.name]

        enum = Enum(name, list(named_choices), type=EnumWithDescriptionsType)
        return enum(description=field.help_text)
    return convert_django_field(field, registry)


@singledispatch
def convert_django_field(field, registry=None):
    raise Exception(
        "Don't know how to convert the Django field %s (%s)" %
        (field, field.__class__))


@convert_django_field.register(models.CharField)
@convert_django_field.register(models.TextField)
@convert_django_field.register(models.EmailField)
@convert_django_field.register(models.SlugField)
@convert_django_field.register(models.URLField)
@convert_django_field.register(models.GenericIPAddressField)
@convert_django_field.register(models.FileField)
@convert_django_field.register(UUIDField)
def convert_field_to_string(field, registry=None):
    return String(description=field.help_text)


@convert_django_field.register(models.AutoField)
def convert_field_to_id(field, registry=None):
    return ID(description=field.help_text)


@convert_django_field.register(models.PositiveIntegerField)
@convert_django_field.register(models.PositiveSmallIntegerField)
@convert_django_field.register(models.SmallIntegerField)
@convert_django_field.register(models.BigIntegerField)
@convert_django_field.register(models.IntegerField)
def convert_field_to_int(field, registry=None):
    return Int(description=field.help_text)


@convert_django_field.register(models.BooleanField)
def convert_field_to_boolean(field, registry=None):
    return NonNull(Boolean, description=field.help_text)


@convert_django_field.register(models.NullBooleanField)
def convert_field_to_nullboolean(field, registry=None):
    return Boolean(description=field.help_text)


@convert_django_field.register(models.DecimalField)
@convert_django_field.register(models.FloatField)
def convert_field_to_float(field, registry=None):
    return Float(description=field.help_text)


@convert_django_field.register(models.DateField)
def convert_date_to_string(field, registry=None):
    return DateTime(description=field.help_text)


@convert_django_field.register(models.OneToOneRel)
def convert_onetoone_field_to_djangomodel(field, registry=None):
    model = get_related_model(field)

    def dynamic_type():
        _type = registry.get_type_for_model(model)
        if not _type:
            return

        return Field(_type)

    return Dynamic(dynamic_type)


@convert_django_field.register(models.ManyToManyField)
@convert_django_field.register(models.ManyToManyRel)
@convert_django_field.register(models.ManyToOneRel)
def convert_field_to_list_or_connection(field, registry=None):
    model = get_related_model(field)

    def dynamic_type():
        _type = registry.get_type_for_model(model)
        if not _type:
            return

        if is_node(_type):
            return get_connection_field(_type)
        return Field(List(_type))

    return Dynamic(dynamic_type)


# For Django 1.6
@convert_django_field.register(RelatedObject)
def convert_relatedfield_to_djangomodel(field, registry=None):
    model = field.model

    def dynamic_type():
        _type = registry.get_type_for_model(model)
        if not _type:
            return

        if is_node(_type):
            return get_connection_field(_type)
        return Field(List(_type))

    return Dynamic(dynamic_type)


@convert_django_field.register(models.OneToOneField)
@convert_django_field.register(models.ForeignKey)
def convert_field_to_djangomodel(field, registry=None):
    model = get_related_model(field)

    def dynamic_type():
        _type = registry.get_type_for_model(model)
        if not _type:
            return

        return Field(_type, description=field.help_text)

    return Dynamic(dynamic_type)


@convert_django_field.register(ArrayField)
def convert_postgres_array_to_list(field, registry=None):
    base_type = convert_django_field(field.base_field)
    if not isinstance(base_type, (List, NonNull)):
        base_type = type(base_type)
    return List(base_type, description=field.help_text)


@convert_django_field.register(HStoreField)
@convert_django_field.register(JSONField)
def convert_posgres_field_to_string(field, registry=None):
    return JSONString(description=field.help_text)


@convert_django_field.register(RangeField)
def convert_posgres_range_to_string(field, registry=None):
    inner_type = convert_django_field(field.base_field)
    if not isinstance(inner_type, (List, NonNull)):
        inner_type = type(inner_type)
    return List(inner_type, description=field.help_text)
