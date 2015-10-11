from singledispatch import singledispatch
from django.db import models

from graphene.core.fields import (
    StringField,
    IDField,
    IntField,
    BooleanField,
    FloatField,
    ListField
)
from graphene.contrib.django.fields import ConnectionOrListField, DjangoModelField


@singledispatch
def convert_django_field(field):
    raise Exception(
        "Don't know how to convert the Django field %s (%s)" % (field, field.__class__))


@convert_django_field.register(models.DateField)
@convert_django_field.register(models.CharField)
@convert_django_field.register(models.TextField)
@convert_django_field.register(models.EmailField)
@convert_django_field.register(models.SlugField)
@convert_django_field.register(models.URLField)
@convert_django_field.register(models.UUIDField)
def _(field):
    return StringField(description=field.help_text)


@convert_django_field.register(models.AutoField)
def _(field):
    return IDField(description=field.help_text)


@convert_django_field.register(models.PositiveIntegerField)
@convert_django_field.register(models.PositiveSmallIntegerField)
@convert_django_field.register(models.SmallIntegerField)
@convert_django_field.register(models.BigIntegerField)
@convert_django_field.register(models.IntegerField)
def _(field):
    return IntField(description=field.help_text)


@convert_django_field.register(models.BooleanField)
def _(field):
    return BooleanField(description=field.help_text, required=True)


@convert_django_field.register(models.NullBooleanField)
def _(field):
    return BooleanField(description=field.help_text)


@convert_django_field.register(models.FloatField)
def _(field):
    return FloatField(description=field.help_text)


@convert_django_field.register(models.ManyToManyField)
@convert_django_field.register(models.ManyToOneRel)
def _(field):
    model_field = DjangoModelField(field.related_model)
    return ConnectionOrListField(model_field)


@convert_django_field.register(models.OneToOneField)
@convert_django_field.register(models.ForeignKey)
def _(field):
    return DjangoModelField(field.related_model, description=field.help_text)
