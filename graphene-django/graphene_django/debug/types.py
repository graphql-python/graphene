from graphene import ObjectType, List
from .sql.types import DjangoDebugBaseSQL


class DjangoDebug(ObjectType):
    sql = List(DjangoDebugBaseSQL)
