import pytest
from django.db import models
from django.utils.translation import ugettext_lazy as _
from py.test import raises

import graphene
from graphene.relay import Node, ConnectionField
from graphene.types.datetime import DateTime
from graphene.utils.get_graphql_type import get_graphql_type
# from graphene.core.types.custom_scalars import DateTime, JSONString

from ..compat import (ArrayField, HStoreField, JSONField, MissingType,
                      RangeField)
from ..converter import convert_django_field, convert_django_field_with_choices
from ..registry import Registry
from .models import Article, Reporter, Film, FilmDetails, Pet
from ..types import DjangoObjectType, DjangoNode


def assert_conversion(django_field, graphene_field, *args, **kwargs):
    field = django_field(help_text='Custom Help Text', *args, **kwargs)
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
    assert_conversion(models.DateField, DateTime)


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


def test_should_ipaddress_convert_string():
    assert_conversion(models.GenericIPAddressField, graphene.String)


def test_should_file_convert_string():
    assert_conversion(models.FileField, graphene.String)


def test_should_image_convert_string():
    assert_conversion(models.ImageField, graphene.String)


def test_should_auto_convert_id():
    assert_conversion(models.AutoField, graphene.ID, primary_key=True)


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


def test_field_with_choices_convert_enum():
    field = models.CharField(help_text='Language', choices=(
        ('es', 'Spanish'),
        ('en', 'English')
    ))

    class TranslatedModel(models.Model):
        language = field

        class Meta:
            app_label = 'test'

    graphene_type = convert_django_field_with_choices(field)
    assert issubclass(graphene_type, graphene.Enum)
    assert graphene_type._meta.graphql_type.name == 'TEST_TRANSLATEDMODEL_LANGUAGE'
    assert graphene_type._meta.graphql_type.description == 'Language'
    assert graphene_type._meta.enum.__members__['SPANISH'].value == 'es'
    assert graphene_type._meta.enum.__members__['ENGLISH'].value == 'en'


def test_field_with_grouped_choices():
    field = models.CharField(help_text='Language', choices=(
        ('Europe', (
            ('es', 'Spanish'),
            ('en', 'English'),
        )),
    ))

    class GroupedChoicesModel(models.Model):
        language = field

        class Meta:
            app_label = 'test'

    convert_django_field_with_choices(field)


def test_field_with_choices_gettext():
    field = models.CharField(help_text='Language', choices=(
        ('es', _('Spanish')),
        ('en', _('English'))
    ))

    class TranslatedChoicesModel(models.Model):
        language = field

        class Meta:
            app_label = 'test'

    convert_django_field_with_choices(field)


def test_should_float_convert_float():
    assert_conversion(models.FloatField, graphene.Float)


def test_should_manytomany_convert_connectionorlist():
    registry = Registry()
    graphene_field = convert_django_field(Reporter._meta.local_many_to_many[0], registry)
    assert not graphene_field


def test_should_manytomany_convert_connectionorlist_list():
    class A(DjangoObjectType):
        class Meta:
            model = Reporter

    graphene_field = convert_django_field(Reporter._meta.local_many_to_many[0], A._meta.registry)
    assert isinstance(graphene_field, graphene.Field)
    assert isinstance(graphene_field.type, graphene.List)
    assert graphene_field.type.of_type == get_graphql_type(A)


def test_should_manytomany_convert_connectionorlist_connection():
    class A(DjangoNode, DjangoObjectType):
        class Meta:
            model = Reporter

    graphene_field = convert_django_field(Reporter._meta.local_many_to_many[0], A._meta.registry)
    assert isinstance(graphene_field, ConnectionField)
    assert graphene_field.type == get_graphql_type(A.get_default_connection())


def test_should_manytoone_convert_connectionorlist():
    # Django 1.9 uses 'rel', <1.9 uses 'related
    related = getattr(Reporter.articles, 'rel', None) or \
        getattr(Reporter.articles, 'related')

    class A(DjangoObjectType):
        class Meta:
            model = Article

    graphene_field = convert_django_field(related, A._meta.registry)
    assert isinstance(graphene_field, graphene.Field)
    assert isinstance(graphene_field.type, graphene.List)
    assert graphene_field.type.of_type == get_graphql_type(A)


def test_should_onetoone_reverse_convert_model():
    # Django 1.9 uses 'rel', <1.9 uses 'related
    related = getattr(Film.details, 'rel', None) or \
        getattr(Film.details, 'related')

    class A(DjangoObjectType):
        class Meta:
            model = FilmDetails

    graphene_field = convert_django_field(related, A._meta.registry)
    assert isinstance(graphene_field, graphene.Field)
    assert graphene_field.type == get_graphql_type(A)


@pytest.mark.skipif(ArrayField is MissingType,
                    reason="ArrayField should exist")
def test_should_postgres_array_convert_list():
    field = assert_conversion(ArrayField, graphene.List, models.CharField(max_length=100))
    assert isinstance(field.type, graphene.List)
    assert isinstance(field.type.of_type, graphene.String)


@pytest.mark.skipif(ArrayField is MissingType,
                    reason="ArrayField should exist")
def test_should_postgres_array_multiple_convert_list():
    field = assert_conversion(ArrayField, graphene.List, ArrayField(models.CharField(max_length=100)))
    assert isinstance(field.type, graphene.List)
    assert isinstance(field.type.of_type, graphene.List)
    assert isinstance(field.type.of_type.of_type, graphene.String)


@pytest.mark.skipif(HStoreField is MissingType,
                    reason="HStoreField should exist")
def test_should_postgres_hstore_convert_string():
    assert_conversion(HStoreField, JSONString)


@pytest.mark.skipif(JSONField is MissingType,
                    reason="JSONField should exist")
def test_should_postgres_json_convert_string():
    assert_conversion(JSONField, JSONString)


@pytest.mark.skipif(RangeField is MissingType,
                    reason="RangeField should exist")
def test_should_postgres_range_convert_list():
    from django.contrib.postgres.fields import IntegerRangeField
    field = assert_conversion(IntegerRangeField, graphene.List)
    assert isinstance(field.type.of_type, graphene.Int)
