import pytest

from ..argument import Argument
from ..structures import NonNull
from ..scalars import String


def test_argument():
    arg = Argument(String, default_value='a', description='desc', name='b')
    assert arg.type == String
    assert arg.default_value == 'a'
    assert arg.description == 'desc'
    assert arg.name == 'b'


def test_argument_comparasion():
    arg1 = Argument(String, name='Hey', description='Desc', default_value='default')
    arg2 = Argument(String, name='Hey', description='Desc', default_value='default')

    assert arg1 == arg2
    assert arg1 != String()


def test_argument_required():
    arg = Argument(String, required=True)
    assert arg.type == NonNull(String)
