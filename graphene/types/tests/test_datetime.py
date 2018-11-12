import datetime

import pytz
from graphql import GraphQLError
import pytest

from ..datetime import Date, DateTime, Time
from ..objecttype import ObjectType
from ..schema import Schema


class Query(ObjectType):
    datetime = DateTime(_in=DateTime(name="in"))
    date = Date(_in=Date(name="in"))
    time = Time(_at=Time(name="at"))

    def resolve_datetime(self, info, _in=None):
        return _in

    def resolve_date(self, info, _in=None):
        return _in

    def resolve_time(self, info, _at=None):
        return _at


schema = Schema(query=Query)


def test_datetime_query():
    now = datetime.datetime.now().replace(tzinfo=pytz.utc)
    isoformat = now.isoformat()

    result = schema.execute("""{ datetime(in: "%s") }""" % isoformat)
    assert not result.errors
    assert result.data == {"datetime": isoformat}


def test_date_query():
    now = datetime.datetime.now().replace(tzinfo=pytz.utc).date()
    isoformat = now.isoformat()

    result = schema.execute("""{ date(in: "%s") }""" % isoformat)
    assert not result.errors
    assert result.data == {"date": isoformat}


def test_time_query():
    now = datetime.datetime.now().replace(tzinfo=pytz.utc)
    time = datetime.time(now.hour, now.minute, now.second, now.microsecond, now.tzinfo)
    isoformat = time.isoformat()

    result = schema.execute("""{ time(at: "%s") }""" % isoformat)
    assert not result.errors
    assert result.data == {"time": isoformat}


def test_bad_datetime_query():
    not_a_date = "Some string that's not a date"

    result = schema.execute("""{ datetime(in: "%s") }""" % not_a_date)

    assert len(result.errors) == 1
    assert isinstance(result.errors[0], GraphQLError)
    assert result.data is None


def test_bad_date_query():
    not_a_date = "Some string that's not a date"

    result = schema.execute("""{ date(in: "%s") }""" % not_a_date)

    assert len(result.errors) == 1
    assert isinstance(result.errors[0], GraphQLError)
    assert result.data is None


def test_bad_time_query():
    not_a_date = "Some string that's not a date"

    result = schema.execute("""{ time(at: "%s") }""" % not_a_date)

    assert len(result.errors) == 1
    assert isinstance(result.errors[0], GraphQLError)
    assert result.data is None


def test_datetime_query_variable():
    now = datetime.datetime.now().replace(tzinfo=pytz.utc)
    isoformat = now.isoformat()

    # test datetime variable provided as Python datetime
    result = schema.execute(
        """query Test($date: DateTime){ datetime(in: $date) }""",
        variables={"date": now},
    )
    assert not result.errors
    assert result.data == {"datetime": isoformat}

    # test datetime variable in string representation
    result = schema.execute(
        """query Test($date: DateTime){ datetime(in: $date) }""",
        variables={"date": isoformat},
    )
    assert not result.errors
    assert result.data == {"datetime": isoformat}


def test_date_query_variable():
    now = datetime.datetime.now().replace(tzinfo=pytz.utc).date()
    isoformat = now.isoformat()

    # test date variable provided as Python date
    result = schema.execute(
        """query Test($date: Date){ date(in: $date) }""", variables={"date": now}
    )
    assert not result.errors
    assert result.data == {"date": isoformat}

    # test date variable in string representation
    result = schema.execute(
        """query Test($date: Date){ date(in: $date) }""", variables={"date": isoformat}
    )
    assert not result.errors
    assert result.data == {"date": isoformat}


def test_time_query_variable():
    now = datetime.datetime.now().replace(tzinfo=pytz.utc)
    time = datetime.time(now.hour, now.minute, now.second, now.microsecond, now.tzinfo)
    isoformat = time.isoformat()

    # test time variable provided as Python time
    result = schema.execute(
        """query Test($time: Time){ time(at: $time) }""", variables={"time": time}
    )
    assert not result.errors
    assert result.data == {"time": isoformat}

    # test time variable in string representation
    result = schema.execute(
        """query Test($time: Time){ time(at: $time) }""", variables={"time": isoformat}
    )
    assert not result.errors
    assert result.data == {"time": isoformat}


@pytest.mark.xfail(reason="creating the error message fails when un-parsable object is not JSON serializable.")
def test_bad_variables():
    def _test_bad_variables(type, input):
        result = schema.execute(
            """query Test($input: %s){ %s(in: $input) }""" % (type, type.lower()),
            variables={"input": input}
        )
        assert len(result.errors) == 1
        # when `input` is not JSON serializable formatting the error message in
        # `graphql.utils.is_valid_value` line 79 fails with a TypeError
        assert isinstance(result.errors[0], GraphQLError)
        print(result.errors[0])
        assert result.data is None

    not_a_date = dict()
    not_a_date_str = "Some string that's not a date"
    today = datetime.date.today()
    now = datetime.datetime.now().replace(tzinfo=pytz.utc)
    time = datetime.time(now.hour, now.minute, now.second, now.microsecond, now.tzinfo)

    bad_pairs = [
        ('DateTime', not_a_date), ('DateTime', not_a_date_str), ('DateTime', today), ('DateTime', time),
        ('Date', not_a_date), ('Date', not_a_date_str), ('Date', now), ('Date', time),
        ('Time', not_a_date), ('Time', not_a_date_str), ('Time', now), ('Time', today)
    ]

    for type, input in bad_pairs:
        _test_bad_variables(type, input)
