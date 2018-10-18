from functools import partial

import pytest
from graphql.error import GraphQLError

from ..argument import Argument
from ..field import Field
from ..scalars import String
from ..structures import NonNull
from .utils import MyLazyType


class MyInstance(object):
    value = "value"
    value_func = staticmethod(lambda: "value_func")

    def value_method(self):
        return "value_method"


class AlwaysFalsePermission(object):
    def has_permission(self, info, field):
        return False

class AlwaysTruePermission(object):
    def has_permission(self, info, field):
        return True


def test_raises_error():
    MyType = object()
    field = Field(MyType, source="value", permission_classes=[AlwaysFalsePermission])

    with pytest.raises(GraphQLError):

        field.get_resolver(None)(MyInstance(), None)

        # TODO: test error message

def test_does_not_raise_error():
    MyType = object()
    field = Field(MyType, source="value", permission_classes=[AlwaysTruePermission])

    field.get_resolver(None)(MyInstance(), None)
