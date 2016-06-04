import inspect
from ..types.objecttype import ObjectType
from ..types.interface import Interface
from ..types.scalars import Scalar


def is_graphene_type(_type):
    return inspect.isclass(_type) and issubclass(_type, (
        Interface,
        ObjectType,
        Scalar
    ))
