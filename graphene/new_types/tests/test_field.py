import pytest

from ..field import Field
from ..structures import NonNull
from ..argument import Argument


class MyInstance(object):
    value = 'value'
    value_func = staticmethod(lambda: 'value_func')


def test_field_basic():
    MyType = object()
    args = {'my arg': Argument(True)}
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
    assert str(exc_info.value) == 'A Field cannot have a source and a resolver in at the same time.'


def test_field_source_func():
    MyType = object()
    field = Field(MyType, source='value_func')
    assert field.resolver(MyInstance(), {}, None, None) == MyInstance.value_func()


def test_field_source_argument_as_kw():
    MyType = object()
    field = Field(MyType, b=NonNull(True), c=Argument(None), a=NonNull(False))
    assert field.args.keys() == ['b', 'c', 'a']
    assert isinstance(field.args['b'], Argument)
    assert isinstance(field.args['b'].type, NonNull)
    assert field.args['b'].type.of_type is True
    assert isinstance(field.args['c'], Argument)
    assert field.args['c'].type is None
    assert isinstance(field.args['a'], Argument)
    assert isinstance(field.args['a'].type, NonNull)
    assert field.args['a'].type.of_type is False
