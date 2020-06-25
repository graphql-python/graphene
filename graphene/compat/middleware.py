from graphql import OperationType

from ..utils.str_converters import to_snake_case
from ..types.definitions import GrapheneEnumType, GrapheneInputObjectType
from ..types.utils import get_underlying_type


def convert_enum_args(args, input_arguments):
    new_args = {}

    for arg_name, arg in input_arguments.items():
        _type = get_underlying_type(arg.type)

        arg_name = to_snake_case(arg_name)
        input_value = args.get(arg_name, None)

        if isinstance(_type, GrapheneEnumType):
            # Convert inputs to value
            if input_value and isinstance(input_value, _type.graphene_type._meta.enum):
                new_args[arg_name] = input_value.value
            else:
                new_args[arg_name] = input_value
        elif isinstance(_type, GrapheneInputObjectType):
            _input_arguments = get_underlying_type(arg.type).fields
            input_type = input_value.get_type()
            new_args[arg_name] = input_type(
                **convert_enum_args(input_value, _input_arguments)
            )
        else:
            new_args[arg_name] = input_value

    return new_args


def enum_value_convertor_middleware(next, root, info, **args):
    """
    Compatibility middleware for upgrading to v3:

    Convert enums to their values for mutation inputs, like the behaviour in v2
    """
    operation = info.operation.operation
    if operation == OperationType.MUTATION:
        input_arguments = info.parent_type.fields[info.field_name].args

        new_args = convert_enum_args(args, input_arguments)

    return next(root, info, **new_args)
