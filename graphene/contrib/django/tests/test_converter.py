from django.db import models
from py.test import raises

import graphene
from graphene.contrib.django.converter import convert_django_field
from graphene.contrib.django.fields import (ConnectionOrListField,
                                            DjangoModelField)

from .models import Article, Reporter


def assert_conversion(django_field, graphene_field, *args):
    field = django_field(*args, help_text='Custom Help Text')
    graphene_type = convert_django_field(field)
    assert isinstance(graphene_type, graphene_field)
    field = graphene_type.as_field()
    assert field.description == 'Custom Help Text'
    return field


def test_should_unknown_django_field_raise_exception():
    with raises(Exception) as excinfo:
        convert_django_field(None)
    assert 'Don\'t know how to convert the Django field' in str(excinfo.value)


def test_should_date_convert_string():
    assert_conversion(models.DateField, graphene.String)


def test_should_char_convert_string():
    assert_conversion(models.CharField, graphene.String)


def test_should_text_convert_string():
    assert_conversion(models.TextField, graphene.String)


def test_should_email_convert_string():
    assert_conversion(models.EmailField, graphene.String)


def test_should_slug_convert_string():
    assert_conversion(models.SlugField, graphene.String)


def test_should_url_convert_string():
    assert_conversion(models.URLField, graphene.String)


def test_should_auto_convert_id():
    assert_conversion(models.AutoField, graphene.ID)


def test_should_positive_integer_convert_int():
    assert_conversion(models.PositiveIntegerField, graphene.Int)


def test_should_positive_small_convert_int():
    assert_conversion(models.PositiveSmallIntegerField, graphene.Int)


def test_should_small_integer_convert_int():
    assert_conversion(models.SmallIntegerField, graphene.Int)


def test_should_big_integer_convert_int():
    assert_conversion(models.BigIntegerField, graphene.Int)


def test_should_integer_convert_int():
    assert_conversion(models.IntegerField, graphene.Int)


def test_should_boolean_convert_boolean():
    field = assert_conversion(models.BooleanField, graphene.Boolean)
    assert field.required is True


def test_should_nullboolean_convert_boolean():
    field = assert_conversion(models.NullBooleanField, graphene.Boolean)
    assert field.required is False


def test_should_float_convert_float():
    assert_conversion(models.FloatField, graphene.Float)


def test_should_manytomany_convert_connectionorlist():
    graphene_type = convert_django_field(Reporter._meta.local_many_to_many[0])
    assert isinstance(graphene_type, ConnectionOrListField)
    assert isinstance(graphene_type.type, DjangoModelField)
    assert graphene_type.type.model == Reporter


def test_should_manytoone_convert_connectionorlist():
    graphene_type = convert_django_field(Reporter.articles.related)
    assert isinstance(graphene_type, ConnectionOrListField)
    assert isinstance(graphene_type.type, DjangoModelField)
    assert graphene_type.type.model == Article


def test_should_onetoone_convert_model():
    field = assert_conversion(models.OneToOneField, DjangoModelField, Article)
    assert field.type.model == Article


def test_should_foreignkey_convert_model():
    field = assert_conversion(models.ForeignKey, DjangoModelField, Article)
    assert field.type.model == Article
