from django import forms
from django.forms.fields import BaseTemporalField
from singledispatch import singledispatch

from graphene import String, Int, Boolean, Float, ID
from .converter import UUIDFormField


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
@convert_form_field.register(UUIDFormField)
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
def convert_form_field_to_list_or_connection(field):
    # TODO: Consider how filtering on a many-to-many should work
    from .fields import DjangoModelField, ConnectionOrListField
    model_field = DjangoModelField(field.queryset.model)
    return ConnectionOrListField(model_field)


@convert_form_field.register(forms.ModelChoiceField)
def convert_form_field_to_djangomodel(field):
    return ID()
    # return DjangoModelField(field.queryset.model, description=field.help_text)
