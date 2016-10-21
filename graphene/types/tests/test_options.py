import pytest

from ..options import Options


def test_options():
    class BaseOptions:
        option_1 = False
        name = True
    meta = Options(BaseOptions, name=False, option_1=False)
    assert meta.name == True
    assert meta.option_1 == False


def test_options_extra_attrs():
    class BaseOptions:
        name = True
        type = True
    
    with pytest.raises(Exception) as exc_info:
        meta = Options(BaseOptions)

    assert str(exc_info.value) == 'Invalid attributes: name, type'


def test_options_repr():
    class BaseOptions:
        name = True
    meta = Options(BaseOptions, name=False)
    assert repr(meta) == '<Options name=True>'
