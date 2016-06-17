from .....core import Boolean, Float, ObjectType, String


class DjangoDebugBaseSQL(ObjectType):
    vendor = String()
    alias = String()
    sql = String()
    duration = Float()
    raw_sql = String()
    params = String()
    start_time = Float()
    stop_time = Float()
    is_slow = Boolean()
    is_select = Boolean()


class DjangoDebugSQL(DjangoDebugBaseSQL):
    pass


class DjangoDebugPostgreSQL(DjangoDebugBaseSQL):
    trans_id = String()
    trans_status = String()
    iso_level = String()
    encoding = String()
