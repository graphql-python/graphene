from collections import OrderedDict

from graphql.type import GraphQLEnumValue


def values_from_enum(enum):
    _values = OrderedDict()
    for name, value in enum.__members__.items():
        _values[name] = GraphQLEnumValue(
            name=name,
            value=value.value,
            description=getattr(value, 'description', None),
            deprecation_reason=getattr(value, 'deprecation_reason', None)
        )
    return _values
