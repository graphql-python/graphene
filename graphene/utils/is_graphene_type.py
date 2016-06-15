import inspect


def is_graphene_type(_type):
    from ..types.objecttype import ObjectType
    from ..types.mutation import Mutation
    from ..types.inputobjecttype import InputObjectType
    from ..types.interface import Interface
    from ..types.scalars import Scalar
    from ..types.enum import Enum
    from ..relay.mutation import ClientIDMutation

    if _type in [Interface, InputObjectType, ObjectType, Mutation, ClientIDMutation]:
        return False
    return inspect.isclass(_type) and issubclass(_type, (
        Interface,
        ObjectType,
        InputObjectType,
        Scalar,
        Mutation,
        Enum
    ))
