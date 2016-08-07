import inspect


def is_graphene_type(_type):
    from ..types.objecttype import ObjectType
    from ..types.mutation import Mutation
    from ..types.inputobjecttype import InputObjectType
    from ..types.interface import Interface
    from ..types.scalars import Scalar
    from ..types.enum import Enum

    return inspect.isclass(_type) and hasattr(_type, '_meta') and issubclass(_type, (
        Interface,
        ObjectType,
        InputObjectType,
        Scalar,
        Mutation,
        Enum
    ))
