import iso8601
from graphql.language.ast import StringValue

from ..custom_scalars import DateTime


def test_date_time():
    test_iso_string = "2016-04-29T18:34:12.502Z"

    def check_datetime(test_dt):
        assert test_dt.tzinfo == iso8601.UTC
        assert test_dt.year == 2016
        assert test_dt.month == 4
        assert test_dt.day == 29
        assert test_dt.hour == 18
        assert test_dt.minute == 34
        assert test_dt.second == 12

    test_dt = DateTime().parse_value(test_iso_string)
    check_datetime(test_dt)

    assert DateTime.serialize(test_dt) == "2016-04-29T18:34:12.502000+00:00"

    node = StringValue(test_iso_string)
    test_dt = DateTime.parse_literal(node)
    check_datetime(test_dt)
