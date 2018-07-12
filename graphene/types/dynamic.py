import inspect
from functools import partial

from .mountedtype import MountedType

from ..utils.comparison_helper import raise_assertion_if


class Dynamic(MountedType):
    """
    A Dynamic Type let us get the type in runtime when we generate
    the schema. So we can have lazy fields.
    """

    def __init__(self, type, with_schema=False, _creation_counter=None):
        super(Dynamic, self).__init__(_creation_counter=_creation_counter)
        raise_assertion_if(
            condition=not (inspect.isfunction(type) or isinstance(type, partial)),
            message="type is expected to be a function or an instance of partial"
        )
        self.type = type
        self.with_schema = with_schema

    def get_type(self, schema=None):
        if schema and self.with_schema:
            return self.type(schema=schema)
        return self.type()
