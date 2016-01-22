from django import forms
from py.test import raises

import graphene
from graphene.contrib.django.form_converter import convert_form_field
from graphene.core.types import ID, List

from .models import Reporter


def assert_conversion(django_field, graphene_field, *args):
    field = django_field(*args, help_text='Custom Help Text')
    graphene_type = convert_form_field(field)
    assert isinstance(graphene_type, graphene_field)
    field = graphene_type.as_field()
    assert field.description == 'Custom Help Text'
    return field


def test_should_unknown_django_field_raise_exception():
    with raises(Exception) as excinfo:
        convert_form_field(None)
    assert 'Don\'t know how to convert the Django form field' in str(excinfo.value)


def test_should_date_convert_string():
    assert_conversion(forms.DateField, graphene.String)


def test_should_time_convert_string():
    assert_conversion(forms.TimeField, graphene.String)


def test_should_date_time_convert_string():
    assert_conversion(forms.DateTimeField, graphene.String)


def test_should_char_convert_string():
    assert_conversion(forms.CharField, graphene.String)


def test_should_email_convert_string():
    assert_conversion(forms.EmailField, graphene.String)


def test_should_slug_convert_string():
    assert_conversion(forms.SlugField, graphene.String)


def test_should_url_convert_string():
    assert_conversion(forms.URLField, graphene.String)


def test_should_choice_convert_string():
    assert_conversion(forms.ChoiceField, graphene.String)


def test_should_base_field_convert_string():
    assert_conversion(forms.Field, graphene.String)


def test_should_regex_convert_string():
    assert_conversion(forms.RegexField, graphene.String, '[0-9]+')


def test_should_uuid_convert_string():
    if hasattr(forms, 'UUIDField'):
        assert_conversion(forms.UUIDField, graphene.String)


def test_should_integer_convert_int():
    assert_conversion(forms.IntegerField, graphene.Int)


def test_should_boolean_convert_boolean():
    field = assert_conversion(forms.BooleanField, graphene.Boolean)
    assert field.required is True


def test_should_nullboolean_convert_boolean():
    field = assert_conversion(forms.NullBooleanField, graphene.Boolean)
    assert field.required is False


def test_should_float_convert_float():
    assert_conversion(forms.FloatField, graphene.Float)


def test_should_decimal_convert_float():
    assert_conversion(forms.DecimalField, graphene.Float)


def test_should_multiple_choice_convert_connectionorlist():
    field = forms.ModelMultipleChoiceField(Reporter.objects.all())
    graphene_type = convert_form_field(field)
    assert isinstance(graphene_type, List)
    assert isinstance(graphene_type.of_type, ID)


def test_should_manytoone_convert_connectionorlist():
    field = forms.ModelChoiceField(Reporter.objects.all())
    graphene_type = convert_form_field(field)
    assert isinstance(graphene_type, graphene.ID)
