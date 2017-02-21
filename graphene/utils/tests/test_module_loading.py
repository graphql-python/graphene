from pytest import raises

from graphene import String
from ..module_loading import lazy_import, import_string


def test_import_string():
    MyString = import_string('graphene.String')
    assert MyString == String


def test_import_string_module():
    with raises(Exception) as exc_info:
        import_string('graphenea')

    assert str(exc_info.value) == 'graphenea doesn\'t look like a module path'


def test_import_string_class():
    with raises(Exception) as exc_info:
        import_string('graphene.Stringa')

    assert str(exc_info.value) == 'Module "graphene" does not define a "Stringa" attribute/class'


def test_lazy_import():
    f = lazy_import('graphene.String')
    MyString = f()
    assert MyString == String
