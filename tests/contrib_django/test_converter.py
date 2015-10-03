from py.test import raises
from collections import namedtuple
from pytest import raises
import graphene
from graphene import relay
from graphene.contrib.django.converter import (
    convert_django_field
)
from graphene.contrib.django.fields import (
    ConnectionOrListField,
    DjangoModelField
)
from django.db import models
from .models import Article, Reporter


def assert_conversion(django_field, graphene_field, *args):
    field = django_field(*args)
    graphene_type = convert_django_field(field)
    assert isinstance(graphene_type, graphene_field)
    return graphene_type


def test_should_unknown_django_field_raise_exception():
    with raises(Exception) as excinfo:
        convert_django_field(None)
    assert 'Don\'t know how to convert the Django field' in str(excinfo.value)


def test_should_date_convert_string():
    assert_conversion(models.DateField, graphene.StringField)


def test_should_char_convert_string():
    assert_conversion(models.CharField, graphene.StringField)


def test_should_text_convert_string():
    assert_conversion(models.TextField, graphene.StringField)


def test_should_email_convert_string():
    assert_conversion(models.EmailField, graphene.StringField)


def test_should_slug_convert_string():
    assert_conversion(models.SlugField, graphene.StringField)


def test_should_url_convert_string():
    assert_conversion(models.URLField, graphene.StringField)


def test_should_auto_convert_id():
    assert_conversion(models.AutoField, graphene.IDField)


def test_should_positive_integer_convert_int():
    assert_conversion(models.PositiveIntegerField, graphene.IntField)


def test_should_positive_small_convert_int():
    assert_conversion(models.PositiveSmallIntegerField, graphene.IntField)


def test_should_small_integer_convert_int():
    assert_conversion(models.SmallIntegerField, graphene.IntField)


def test_should_big_integer_convert_int():
    assert_conversion(models.BigIntegerField, graphene.IntField)


def test_should_integer_convert_int():
    assert_conversion(models.IntegerField, graphene.IntField)


def test_should_boolean_convert_boolean():
    assert_conversion(models.BooleanField, graphene.BooleanField)


def test_should_nullboolean_convert_boolean():
    field = assert_conversion(models.NullBooleanField, graphene.BooleanField)
    assert field.null == True


def test_should_float_convert_float():
    assert_conversion(models.FloatField, graphene.FloatField)


def test_should_manytomany_convert_connectionorlist():
    field = assert_conversion(models.ManyToManyField, ConnectionOrListField, Article)


def test_should_manytoone_convert_connectionorlist():
    graphene_type = convert_django_field(Reporter.articles.related)
    assert isinstance(graphene_type, ConnectionOrListField)


def test_should_onetoone_convert_model():
    assert_conversion(models.OneToOneField, DjangoModelField, Article)


def test_should_onetoone_convert_model():
    assert_conversion(models.ForeignKey, DjangoModelField, Article)
