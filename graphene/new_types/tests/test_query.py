from collections import OrderedDict

from py.test import raises

from ..objecttype import ObjectType
from ..scalars import String, Int, Boolean
from ..field import Field
from ..structures import List

from ..schema import Schema


class Query(ObjectType):
    hello = String(resolver=lambda *_: 'World')


def test_query():
    hello_schema = Schema(Query)

    executed = hello_schema.execute('{ hello }')
    print executed.errors
