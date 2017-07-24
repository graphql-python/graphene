from ..pyutils.compat import signature
from functools import wraps, partial


def resolver_from_annotations(func):
    from ..types import Context, ResolveInfo

    func_signature = signature(func)

    _context_var = None
    _info_var = None
    for key, parameter in func_signature.parameters.items():
        param_type = parameter.annotation
        if param_type is Context:
            _context_var = key
        elif param_type is ResolveInfo:
            _info_var = key
        continue

    # We generate different functions as it will be faster
    # than calculating the args on the fly when executing
    # the function resolver.
    if _context_var and _info_var:
        def inner(root, args, context, info):
            return func(root, **dict(args, **{_info_var: info, _context_var: context}))
    elif _context_var:
        def inner(root, args, context, info):
            return func(root, **dict(args, **{_context_var: context}))
    elif _info_var:
        def inner(root, args, context, info):
            return func(root, **dict(args, **{_info_var: info}))
    else:
        def inner(root, args, context, info):
            return func(root, **args)

    if isinstance(func, partial):
        return inner

    return wraps(func)(inner)
