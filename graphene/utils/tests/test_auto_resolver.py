import pytest
from ..annotate import annotate
from ..auto_resolver import auto_resolver, final_resolver

from ...types import Context, ResolveInfo


@final_resolver
def resolver(root, args, context, info):
    return root, args, context, info


def resolver_annotated(root, **args):
    return root, args, None, None


@annotate(context=Context, info=ResolveInfo)
def resolver_with_context_and_info(root, context, info, **args):
    return root, args, context, info


def test_auto_resolver_non_annotated():
    decorated_resolver = auto_resolver(resolver)
    # We make sure the function is not wrapped
    assert decorated_resolver == resolver
    assert decorated_resolver(1, {}, 2, 3) == (1, {}, 2, 3)


def test_auto_resolver_annotated():
    decorated_resolver = auto_resolver(resolver_annotated)
    assert decorated_resolver(1, {}, 2, 3) == (1, {}, None, None)


def test_auto_resolver_annotated_with_context_and_info():
    decorated_resolver = auto_resolver(resolver_with_context_and_info)
    assert decorated_resolver(1, {}, 2, 3) == (1, {}, 2, 3)
