from graphene import ObjectType, List
from .sql.types import DjangoDebugSQL


class DjangoDebug(ObjectType):
    sql = List(DjangoDebugSQL)
