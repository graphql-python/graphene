from .. import deprecated
from ..deprecated import warn_deprecation


def test_warn_deprecation(mocker):
    mocker.patch.object(deprecated, "warn")

    warn_deprecation("OH!")
    deprecated.warn.assert_called_with("OH!", stacklevel=2, category=DeprecationWarning)
