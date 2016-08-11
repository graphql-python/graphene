import pytest

from ..field import Field
from ..structures import NonNull


class MyInstance(object):
    value = 'value'
    value_func = staticmethod(lambda: 'value_func')


def test_field_basic():
    MyType = object()
    args = {}
    resolver = lambda: None
    deprecation_reason = 'Deprecated now'
    description = 'My Field'
    field = Field(
        MyType,
        name='name',
        args=args,
        resolver=resolver,
        description=description,
        deprecation_reason=deprecation_reason
    )
    assert field.name == 'name'
    assert field.args == args
    assert field.resolver == resolver
    assert field.deprecation_reason == deprecation_reason
    assert field.description == description


def test_field_required():
    MyType = object()
    field = Field(MyType, required=True)
    assert isinstance(field.type, NonNull)
    assert field.type.of_type == MyType


def test_field_source():
    MyType = object()
    field = Field(MyType, source='value')
    assert field.resolver(MyInstance, {}, None, None) == MyInstance.value


def test_field_not_source_and_resolver():
    MyType = object()
    with pytest.raises(Exception) as exc_info:
        Field(MyType, source='value', resolver=lambda: None)
    assert str(exc_info.value) == 'You cannot provide a source and a resolver in a Field at the same time.'

def test_field_source_func():
    MyType = object()
    field = Field(MyType, source='value_func')
    assert field.resolver(MyInstance(), {}, None, None) == MyInstance.value_func()
