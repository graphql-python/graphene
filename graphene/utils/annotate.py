import six

from ..pyutils.compat import func_name, signature
from .deprecated import warn_deprecation
from .comparison_helper import raise_assertion_if_true


def annotate(_func=None, _trigger_warning=True, **annotations):
    if not six.PY2 and _trigger_warning:
        warn_deprecation(
            "annotate is intended for use in Python 2 only, as you can use type annotations Python 3.\n"
            "Read more in https://docs.python.org/3/library/typing.html"
        )

    if not _func:

        def _func(f):
            return annotate(f, **annotations)

        return _func

    func_signature = signature(_func)

    # We make sure the annotations are valid
    for key, value in annotations.items():
        func_param = func_signature.parameters.get(key, None)
        assertion_message = 'The key {key} is not a function parameter in the function "{func_name}".'
                                .format(key=key, func_name=func_name(_func)

        raise_assertion_if_true(
            condition=func_param is None,
            message=assertion_message
            )

    func_annotations = getattr(_func, "__annotations__", None)
    if func_annotations is None:
        _func.__annotations__ = annotations
    else:
        _func.__annotations__.update(annotations)

    return _func
