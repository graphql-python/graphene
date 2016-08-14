from py.test import raises

from ..types import SQLAlchemyObjectType

from .models import Reporter
from ..registry import Registry


def test_should_raise_if_no_model():
    with raises(Exception) as excinfo:
        class Character1(SQLAlchemyObjectType):
            pass
    assert 'valid SQLAlchemy Model' in str(excinfo.value)


def test_should_raise_if_model_is_invalid():
    with raises(Exception) as excinfo:
        class Character2(SQLAlchemyObjectType):
            class Meta:
                model = 1
    assert 'valid SQLAlchemy Model' in str(excinfo.value)


def test_should_map_fields_correctly():
    class ReporterType2(SQLAlchemyObjectType):

        class Meta:
            model = Reporter
            registry = Registry()

    assert list(ReporterType2._meta.fields.keys()) == ['id', 'first_name', 'last_name', 'email', 'pets', 'articles']


def test_should_map_only_few_fields():
    class Reporter2(SQLAlchemyObjectType):

        class Meta:
            model = Reporter
            only_fields = ('id', 'email')
    assert list(Reporter2._meta.fields.keys()) == ['id', 'email']
