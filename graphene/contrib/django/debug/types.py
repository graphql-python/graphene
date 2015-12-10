from ....core.classtypes.objecttype import ObjectType
from ....core.types import Field
from .sql.types import DjangoDebugSQL


class DjangoDebug(ObjectType):
    sql = Field(DjangoDebugSQL.List())
