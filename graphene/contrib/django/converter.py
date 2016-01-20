from django.db import models

from ...core.types.scalars import ID, Boolean, Float, Int, String
from .fields import DjangoField, ConnectionOrListField, DjangoModelField
from .compat import RelatedObject, UUIDField
from .utils import get_related_model, import_single_dispatch

singledispatch = import_single_dispatch()


@singledispatch
def convert_django_field(field):
    raise Exception(
        "Don't know how to convert the Django field %s (%s)" %
        (field, field.__class__))


def fetch_field(f):
    def wrapped(field):
        _type = f(field)
        kwargs = dict(_type.kwargs, _field=field)
        return DjangoField(_type, *_type.args, **kwargs)
    return wrapped


@convert_django_field.register(models.DateField)
@convert_django_field.register(models.CharField)
@convert_django_field.register(models.TextField)
@convert_django_field.register(models.EmailField)
@convert_django_field.register(models.SlugField)
@convert_django_field.register(models.URLField)
@convert_django_field.register(models.GenericIPAddressField)
@convert_django_field.register(UUIDField)
@fetch_field
def convert_field_to_string(field):
    return String(description=field.help_text)


@convert_django_field.register(models.AutoField)
@fetch_field
def convert_field_to_id(field):
    return ID(description=field.help_text)


@convert_django_field.register(models.PositiveIntegerField)
@convert_django_field.register(models.PositiveSmallIntegerField)
@convert_django_field.register(models.SmallIntegerField)
@convert_django_field.register(models.BigIntegerField)
@convert_django_field.register(models.IntegerField)
@fetch_field
def convert_field_to_int(field):
    return Int(description=field.help_text)


@convert_django_field.register(models.BooleanField)
@fetch_field
def convert_field_to_boolean(field):
    return Boolean(description=field.help_text, required=True)


@convert_django_field.register(models.NullBooleanField)
@fetch_field
def convert_field_to_nullboolean(field):
    return Boolean(description=field.help_text)


@convert_django_field.register(models.DecimalField)
@convert_django_field.register(models.FloatField)
@fetch_field
def convert_field_to_float(field):
    return Float(description=field.help_text)


@convert_django_field.register(models.ManyToManyField)
@convert_django_field.register(models.ManyToOneRel)
@convert_django_field.register(models.ManyToManyRel)
def convert_field_to_list_or_connection(field):
    model_field = DjangoModelField(get_related_model(field))
    return ConnectionOrListField(model_field, _field=field)


# For Django 1.6
@convert_django_field.register(RelatedObject)
def convert_relatedfield_to_djangomodel(field):
    model_field = DjangoModelField(field.model)
    return ConnectionOrListField(model_field, _field=field)


@convert_django_field.register(models.OneToOneField)
@convert_django_field.register(models.ForeignKey)
def convert_field_to_djangomodel(field):
    related_model = get_related_model(field)
    return DjangoField(DjangoModelField(related_model), description=field.help_text, _field=field)
    # return DjangoModelField(get_related_model(field), description=field.help_text, _field=field)
