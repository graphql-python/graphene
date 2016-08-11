import inspect
from functools import partial
from collections import OrderedDict

# from graphql.type import (GraphQLField, GraphQLInputObjectField)
# from graphql.utils.assert_valid_name import assert_valid_name

from ..utils.orderedtype import OrderedType
from .structures import NonNull
# from ..utils.str_converters import to_camel_case
# from .argument import to_arguments


# class AbstractField(object):

#     @property
#     def name(self):
#         return self._name or self.attname and to_camel_case(self.attname)

#     @name.setter
#     def name(self, name):
#         if name is not None:
#             assert_valid_name(name)
#         self._name = name

#     @property
#     def type(self):
#         from ..utils.get_graphql_type import get_graphql_type
#         from .structures import NonNull
#         if inspect.isfunction(self._type):
#             _type = self._type()
#         else:
#             _type = self._type

#         if self.required:
#             return NonNull(_type)
#         return get_graphql_type(_type)

#     @type.setter
#     def type(self, type):
#         self._type = type

def source_resolver(source, root, args, context, info):
    resolved = getattr(root, source, None)
    if inspect.isfunction(resolved):
        return resolved()
    return resolved


class Field(OrderedType):

    def __init__(self, type, args=None, resolver=None, source=None,
                 deprecation_reason=None, name=None, description=None,
                 required=False, _creation_counter=None, **extra_args):
        super(Field, self).__init__(_creation_counter=_creation_counter)
        self.name = name
        # self.attname = None
        # self.parent = None
        if required:
            type = NonNull(type)
        self._type = type
        self.args = args or OrderedDict()
        # self.args = to_arguments(args, extra_args)
        assert not (source and resolver), ('You cannot provide a source and a '
                                           'resolver in a Field at the same time.')
        if source:
            resolver = partial(source_resolver, source)
        self.resolver = resolver
        self.deprecation_reason = deprecation_reason
        self.description = description

    @property
    def type(self):
        if inspect.isfunction(self._type):
            return self._type()
        return self._type
