import inspect
from typing import List

from graphene.types.field import Field
from graphene.types.inputobjecttype import InputObjectType
from graphene.types.scalars import Scalar
from graphene.types.utils import get_underlying_type
from graphene.utils.str_converters import to_camel_case
from graphene.utils.trim_docstring import trim_docstring


class MutationInvalidArgumentsError(Exception):
    def __init__(self, mutation_name: str, invalid_arguments: List[str]):
        invalid_arguments = sorted(invalid_arguments)

        if len(invalid_arguments) == 1:
            message = (
                f"Argument `{invalid_arguments[0]}` is not a valid type "
                f"in mutation `{mutation_name}`. "
            )
        else:
            head = ", ".join(invalid_arguments[:-1])
            message = (
                f"Arguments `{head}` and `{invalid_arguments[-1]}` are not valid types "
                f"in mutation `{mutation_name}`. "
            )

        message += "Arguments to a mutation need to be either a Scalar type or an InputObjectType."

        super().__init__(message)


def mutation(return_type, arguments=None, **kwargs):
    if arguments is None:
        arguments = {}

    def decorate(resolver_function):
        name = kwargs.pop("name", None) or resolver_function.__name__
        description = kwargs.pop("description", None) or trim_docstring(
            resolver_function.__doc__
        )

        invalid_arguments = []
        for argument_name, argument in arguments.items():
            if inspect.isclass(argument):
                type_ = argument
            else:
                type_ = get_underlying_type(argument.get_type())
            if not (issubclass(type_, Scalar) or issubclass(type_, InputObjectType)):
                invalid_arguments.append(argument_name)

        if len(invalid_arguments) > 0:
            raise MutationInvalidArgumentsError(name, invalid_arguments)

        return Field(
            return_type,
            args=arguments,
            name=to_camel_case(name),
            resolver=resolver_function,
            description=description,
            **kwargs,
        )

    return decorate
