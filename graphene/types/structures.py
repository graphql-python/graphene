import inspect

from graphql import GraphQLList, GraphQLNonNull

from .unmountedtype import UnmountedType


class Structure(UnmountedType):

    def __init__(self, of_type, *args, **kwargs):
        super(Structure, self).__init__(*args, **kwargs)
        self.of_type = of_type

    def get_type(self):
        return self

    @property
    def of_type(self):
        from ..utils.get_graphql_type import get_graphql_type
        if inspect.isfunction(self._of_type):
            return get_graphql_type(self._of_type())
        return get_graphql_type(self._of_type)

    @of_type.setter
    def of_type(self, value):
        self._of_type = value


class List(Structure, GraphQLList):
    pass


class NonNull(Structure, GraphQLNonNull):
    pass
