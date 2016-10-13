import datetime
import pytz

from ..datetime import DateTime
from ..objecttype import ObjectType
from ..schema import Schema


class Query(ObjectType):
    datetime = DateTime(_in=DateTime(name='in'))

    def resolve_datetime(self, args, context, info):
        _in = args.get('in')
        return _in

schema = Schema(query=Query)


def test_datetime_query():
    now = datetime.datetime.now().replace(tzinfo=pytz.utc)
    isoformat = now.isoformat()

    result = schema.execute('''{ datetime(in: "%s") }'''%isoformat)
    assert not result.errors
    assert result.data == {
        'datetime': isoformat
    }


def test_datetime_query_variable():
    now = datetime.datetime.now().replace(tzinfo=pytz.utc)
    isoformat = now.isoformat()

    result = schema.execute(
        '''query Test($date: DateTime){ datetime(in: $date) }''',
        variable_values={'date': isoformat}
    )
    assert not result.errors
    assert result.data == {
        'datetime': isoformat
    }
