from django.core.exceptions import ValidationError
from py.test import raises

from graphene.contrib.django.forms import GlobalIDFormField


# 'TXlUeXBlOjEwMA==' -> 'MyType', 100
# 'TXlUeXBlOmFiYw==' -> 'MyType', 'abc'


def test_global_id_valid():
    field = GlobalIDFormField()
    field.clean('TXlUeXBlOjEwMA==')


def test_global_id_invalid():
    field = GlobalIDFormField()
    with raises(ValidationError):
        field.clean('badvalue')


def test_global_id_none():
    field = GlobalIDFormField()
    with raises(ValidationError):
        field.clean(None)


def test_global_id_none_optional():
    field = GlobalIDFormField(required=False)
    field.clean(None)


def test_global_id_bad_int():
    field = GlobalIDFormField()
    with raises(ValidationError):
        field.clean('TXlUeXBlOmFiYw==')
