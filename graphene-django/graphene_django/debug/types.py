from ....core.classtypes.objecttype import ObjectType
from ....core.types import Field
from .sql.types import DjangoDebugBaseSQL


class DjangoDebug(ObjectType):
    sql = Field(DjangoDebugBaseSQL.List())
