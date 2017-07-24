import pytest
from ..annotate import annotate
from ..resolver_from_annotations import resolver_from_annotations

from ...types import Context, ResolveInfo


@annotate
def func(root, **args):
    return root, args, None, None


@annotate(context=Context)
def func_with_context(root, context, **args):
    return root, args, context, None


@annotate(info=ResolveInfo)
def func_with_info(root, info, **args):
    return root, args, None, info


@annotate(context=Context, info=ResolveInfo)
def func_with_context_and_info(root, context, info, **args):
    return root, args, context, info

root = 1
args = {
    'arg': 0
}
context = 2
info = 3


@pytest.mark.parametrize("func,expected", [
    (func, (1, {'arg': 0}, None, None)),
    (func_with_context, (1, {'arg': 0}, 2, None)),
    (func_with_info, (1, {'arg': 0}, None, 3)),
    (func_with_context_and_info, (1, {'arg': 0}, 2, 3)),
])
def test_resolver_from_annotations(func, expected):
    resolver_func = resolver_from_annotations(func)
    resolved = resolver_func(root, args, context, info)
    assert resolved == expected
