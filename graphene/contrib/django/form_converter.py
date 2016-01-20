from django import forms
from django.forms.fields import BaseTemporalField

from graphene import ID, Boolean, Float, Int, String
from graphene.contrib.django.forms import (GlobalIDFormField,
                                           GlobalIDMultipleChoiceField)
from graphene.contrib.django.utils import import_single_dispatch
from graphene.core.types.definitions import List

singledispatch = import_single_dispatch()

try:
    UUIDField = forms.UUIDField
except AttributeError:
    class UUIDField(object):
        pass


@singledispatch
def convert_form_field(field):
    raise Exception(
        "Don't know how to convert the Django form field %s (%s) "
        "to Graphene type" %
        (field, field.__class__)
    )


@convert_form_field.register(BaseTemporalField)
@convert_form_field.register(forms.CharField)
@convert_form_field.register(forms.EmailField)
@convert_form_field.register(forms.SlugField)
@convert_form_field.register(forms.URLField)
@convert_form_field.register(forms.ChoiceField)
@convert_form_field.register(forms.RegexField)
@convert_form_field.register(forms.Field)
@convert_form_field.register(UUIDField)
def convert_form_field_to_string(field):
    return String(description=field.help_text)


@convert_form_field.register(forms.IntegerField)
@convert_form_field.register(forms.NumberInput)
def convert_form_field_to_int(field):
    return Int(description=field.help_text)


@convert_form_field.register(forms.BooleanField)
@convert_form_field.register(forms.NullBooleanField)
def convert_form_field_to_boolean(field):
    return Boolean(description=field.help_text, required=True)


@convert_form_field.register(forms.NullBooleanField)
def convert_form_field_to_nullboolean(field):
    return Boolean(description=field.help_text)


@convert_form_field.register(forms.DecimalField)
@convert_form_field.register(forms.FloatField)
def convert_form_field_to_float(field):
    return Float(description=field.help_text)


@convert_form_field.register(forms.ModelMultipleChoiceField)
@convert_form_field.register(GlobalIDMultipleChoiceField)
def convert_form_field_to_list(field):
    return List(ID())


@convert_form_field.register(forms.ModelChoiceField)
@convert_form_field.register(GlobalIDFormField)
def convert_form_field_to_id(field):
    return ID()
