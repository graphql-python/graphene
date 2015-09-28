from singledispatch import singledispatch
from django.db import models

from graphene.core.fields import (
    StringField,
    IDField,
    IntField,
    BooleanField,
    FloatField,
)

@singledispatch
def convert_django_field(field):
    raise Exception("Don't know how to convert the Django field %s"%field)


@convert_django_field.register(models.CharField)
def _(field):
    return StringField(description=field.help_text)


@convert_django_field.register(models.AutoField)
def _(field):
    return IDField(description=field.help_text)


@convert_django_field.register(models.BigIntegerField)
@convert_django_field.register(models.IntegerField)
def _(field):
    return IntField(description=field.help_text)


@convert_django_field.register(models.BooleanField)
def _(field):
    return BooleanField(description=field.help_text)


@convert_django_field.register(models.FloatField)
def _(field):
    return FloatField(description=field.help_text)
