import inspect
from ..types.objecttype import ObjectType
from ..types.inputobjecttype import InputObjectType
from ..types.interface import Interface
from ..types.scalars import Scalar
from ..types.enum import Enum


def is_graphene_type(_type):
    if _type in [Interface]:
        return False
    return inspect.isclass(_type) and issubclass(_type, (
        Interface,
        ObjectType,
        InputObjectType,
        Scalar,
        Enum
    ))
