from ..utils.orderedtype import OrderedType
from .structures import NonNull


class InputField(OrderedType):

    def __init__(self, type, name=None, default_value=None,
                 deprecation_reason=None, description=None,
                 required=False, _creation_counter=None, **extra_args):
        super(InputField, self).__init__(_creation_counter=_creation_counter)
        self.name = name
        if required:
            type = NonNull(type)
        self.type = type
        self.deprecation_reason = deprecation_reason
        self.default_value = default_value
        self.description = description
