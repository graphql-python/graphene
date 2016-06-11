import pytest

from ..options import Options


def test_options_defaults():
    class Meta:
        valid_second = True

    options = Options(Meta, valid_second=False, valid_first=False)

    assert not options.valid_first
    assert options.valid_second


def test_options_invalid_attrs():
    class Meta:
        invalid = True

    with pytest.raises(TypeError) as excinfo:
        Options(Meta, valid=True)

    assert "Invalid attributes: invalid" == str(excinfo.value)
