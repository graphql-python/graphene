from graphql import OperationType

from ..utils.str_converters import to_snake_case
from ..types.definitions import GrapheneEnumType
from ..types.utils import get_underlying_type


def enum_value_convertor_middleware(next, root, info, **args):
    """
    Compatibility middleware for upgrading to v3:

    Convert enums to their values for mutation inputs, like the behaviour in v2
    """
    operation = info.operation.operation
    if operation == OperationType.MUTATION:
        input_arguments = info.parent_type.fields[info.field_name].args
        for arg_name, arg in input_arguments.items():
            _type = get_underlying_type(arg.type)
            if isinstance(_type, GrapheneEnumType):
                # Convert inputs to value
                arg_name = to_snake_case(arg_name)
                input_value = args.get(arg_name, None)
                if input_value and isinstance(
                    input_value, _type.graphene_type._meta.enum
                ):
                    args[arg_name] = args[arg_name].value

    return next(root, info, **args)
