from six import PY2
from .annotate import annotate
from .deprecated import deprecated

if PY2:
    deprecation_reason = (
        'Please use @annotate instead.'
    )
else:
    deprecation_reason = (
        'Please use Python 3 type annotations instead. Read more: '
        'https://docs.python.org/3/library/typing.html'
    )


@deprecated(deprecation_reason)
def resolve_only_args(func):
    return annotate(func)
