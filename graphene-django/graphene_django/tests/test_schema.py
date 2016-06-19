from py.test import raises

from ..types import DjangoObjectType
from ..registry import Registry

from .models import Reporter


def test_should_raise_if_no_model():
    with raises(Exception) as excinfo:
        class Character1(DjangoObjectType):
            pass
    assert 'valid Django Model' in str(excinfo.value)


def test_should_raise_if_model_is_invalid():
    with raises(Exception) as excinfo:
        class Character2(DjangoObjectType):

            class Meta:
                model = 1
    assert 'valid Django Model' in str(excinfo.value)


def test_should_map_fields_correctly():
    class ReporterType2(DjangoObjectType):
        class Meta:
            model = Reporter
            registry = Registry()
    assert list(ReporterType2._meta.graphql_type.get_fields().keys()) == ['id', 'firstName', 'lastName', 'email', 'pets', 'aChoice']


def test_should_map_only_few_fields():
    class Reporter2(DjangoObjectType):

        class Meta:
            model = Reporter
            fields = ('id', 'email')

    assert list(Reporter2._meta.graphql_type.get_fields().keys()) == ['id', 'email']
