from graphene.types.field import Field
from graphene.utils.str_converters import to_camel_case


def mutation(return_type, arguments=None, **kwargs):
    # TODO: validate input arguments
    if arguments is None:
        arguments = {}

    def decorate(resolver_function):
        name = kwargs.pop("name", None) or resolver_function.__name__
        description = kwargs.pop("description", None) or resolver_function.__doc__

        return Field(
            return_type,
            args=arguments,
            name=to_camel_case(name),
            resolver=resolver_function,
            description=description,
            **kwargs
        )

    return decorate
