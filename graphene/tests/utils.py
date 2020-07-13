from textwrap import dedent as _dedent


def dedent(text: str) -> str:
    """Fix indentation of given text by removing leading spaces and tabs.
    Also removes leading newlines and trailing spaces and tabs, but keeps trailing
    newlines.
    """
    return _dedent(text.lstrip("\n").rstrip(" \t"))
