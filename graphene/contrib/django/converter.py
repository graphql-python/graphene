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
from graphene.contrib.django.fields import DjangoModelField

@singledispatch
def convert_django_field(field, cls):
    raise Exception("Don't know how to convert the Django field %s (%s)" % (field, field.__class__))


@convert_django_field.register(models.DateField)
@convert_django_field.register(models.CharField)
@convert_django_field.register(models.TextField)
def _(field, cls):
    return StringField(description=field.help_text)


@convert_django_field.register(models.AutoField)
def _(field, cls):
    return IDField(description=field.help_text)


@convert_django_field.register(models.BigIntegerField)
@convert_django_field.register(models.IntegerField)
def _(field, cls):
    return IntField(description=field.help_text)


@convert_django_field.register(models.BooleanField)
def _(field, cls):
    return BooleanField(description=field.help_text)


@convert_django_field.register(models.FloatField)
def _(field, cls):
    return FloatField(description=field.help_text)


@convert_django_field.register(models.ManyToOneRel)
def _(field, cls):
    schema = cls._meta.schema
    model_field = DjangoModelField(field.related_model)
    if issubclass(cls, schema.relay.Node):
        return schema.relay.ConnectionField(model_field)
    return ListField(model_field)


@convert_django_field.register(models.ForeignKey)
def _(field, cls):
    return DjangoModelField(field.related_model)
