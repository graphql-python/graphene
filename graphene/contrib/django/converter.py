from django.db import models
from singledispatch import singledispatch

from ...core.types.scalars import ID, Boolean, Float, Int, String
from .fields import ConnectionOrListField, DjangoModelField

try:
    UUIDField = models.UUIDField
except AttributeError:
    # Improved compatibility for Django 1.6
    class UUIDField(object):
        pass


@singledispatch
def convert_django_field(field):
    raise Exception(
        "Don't know how to convert the Django field %s (%s)" %
        (field, field.__class__))


@convert_django_field.register(models.DateField)
@convert_django_field.register(models.CharField)
@convert_django_field.register(models.TextField)
@convert_django_field.register(models.EmailField)
@convert_django_field.register(models.SlugField)
@convert_django_field.register(models.URLField)
@convert_django_field.register(UUIDField)
def convert_field_to_string(field):
    return String(description=field.help_text)


@convert_django_field.register(models.AutoField)
def convert_field_to_id(field):
    return ID(description=field.help_text)


@convert_django_field.register(models.PositiveIntegerField)
@convert_django_field.register(models.PositiveSmallIntegerField)
@convert_django_field.register(models.SmallIntegerField)
@convert_django_field.register(models.BigIntegerField)
@convert_django_field.register(models.IntegerField)
def convert_field_to_int(field):
    return Int(description=field.help_text)


@convert_django_field.register(models.BooleanField)
def convert_field_to_boolean(field):
    return Boolean(description=field.help_text, required=True)


@convert_django_field.register(models.NullBooleanField)
def convert_field_to_nullboolean(field):
    return Boolean(description=field.help_text)


@convert_django_field.register(models.DecimalField)
@convert_django_field.register(models.FloatField)
def convert_field_to_float(field):
    return Float(description=field.help_text)


@convert_django_field.register(models.ManyToManyField)
@convert_django_field.register(models.ManyToOneRel)
def convert_field_to_list_or_connection(field):
    model_field = DjangoModelField(field.related_model)
    return ConnectionOrListField(model_field)


@convert_django_field.register(models.OneToOneField)
@convert_django_field.register(models.ForeignKey)
def convert_field_to_djangomodel(field):
    return DjangoModelField(field.related_model, description=field.help_text)
