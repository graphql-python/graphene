from warnings import warn


def warn_deprecation(text: str):
    warn(text, category=DeprecationWarning, stacklevel=2)
