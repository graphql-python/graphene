import inspect
from ..types.objecttype import ObjectType
from ..types.inputobjecttype import InputObjectType
from ..types.interface import Interface
from ..types.scalars import Scalar
from ..types.enum import Enum


def is_graphene_type(_type):
    if inspect.isclass(_type):
        return issubclass(_type, (
            Interface,
            ObjectType,
            InputObjectType,
            Scalar,
            Enum
        ))
    return is_graphene_type(type(_type))
