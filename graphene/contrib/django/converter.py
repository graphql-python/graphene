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
def convert_django_field(field, cls):
    raise Exception("Don't know how to convert the Django field %s (%s)" % (field, field.__class__))


@convert_django_field.register(models.DateField)
@convert_django_field.register(models.CharField)
@convert_django_field.register(models.TextField)
@convert_django_field.register(models.EmailField)
@convert_django_field.register(models.SlugField)
@convert_django_field.register(models.URLField)
@convert_django_field.register(models.UUIDField)
def _(field, cls):
    return StringField(description=field.description)


@convert_django_field.register(models.AutoField)
def _(field, cls):
    return IDField(description=field.description)


@convert_django_field.register(models.PositiveIntegerField)
@convert_django_field.register(models.PositiveSmallIntegerField)
@convert_django_field.register(models.SmallIntegerField)
@convert_django_field.register(models.BigIntegerField)
@convert_django_field.register(models.IntegerField)
def _(field, cls):
    return IntField(description=field.description)


@convert_django_field.register(models.BooleanField)
def _(field, cls):
    return BooleanField(description=field.description, null=False)


@convert_django_field.register(models.NullBooleanField)
def _(field, cls):
    return BooleanField(description=field.description)


@convert_django_field.register(models.FloatField)
def _(field, cls):
    return FloatField(description=field.description)


@convert_django_field.register(models.ManyToManyField)
@convert_django_field.register(models.ManyToOneRel)
def _(field, cls):
    model_field = DjangoModelField(field.related_model)
    return ConnectionOrListField(model_field)


@convert_django_field.register(models.OneToOneField)
@convert_django_field.register(models.ForeignKey)
def _(field, cls):
    return DjangoModelField(field.related_model, description=field.description)
