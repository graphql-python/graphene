import pytest

from ..geo import Point
from ..objecttype import ObjectType
from ..schema import Schema


class Query(ObjectType):
    point = Point(input=Point())
    point_list = Point()

    def resolve_point(self, args, context, info):
        input = args.get('input')
        return input

    def resolve_point_list(self, args, context, info):
        return [1, 2]

schema = Schema(query=Query)


@pytest.mark.parametrize("input,expected", [
    ("[1,2]", [1,2]),
    ("[1,2,3]", [1,2,3]),
    ("[]", []),
    (""" "POINT (1 2)" """, [1,2]),
])
def test_point_query(input, expected):
    result = schema.execute('''{ point(input: %s) }'''%(input))
    assert not result.errors
    assert result.data == {
        'point': expected
    }


def test_point_list_query():
    result = schema.execute('''{ pointList }''')
    assert not result.errors
    assert result.data == {
        'pointList': [1, 2]
    }
