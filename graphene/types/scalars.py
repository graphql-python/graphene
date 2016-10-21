import six
import types

from graphql.language.ast import (BooleanValue, FloatValue, IntValue,
                                  StringValue)

from ..utils.is_base_type import is_base_type
from .options import Options
from .unmountedtype import UnmountedType


class ScalarTypeMeta(type):

    def __new__(cls, name, bases, attrs):
        # Also ensure initialization is only performed for subclasses of Model
        # (excluding Model class itself).
        if not is_base_type(bases, ScalarTypeMeta):
            return type.__new__(cls, name, bases, attrs)

        options = Options(
            attrs.pop('Meta', None),
            name=name,
            description=attrs.get('__doc__'),
        )

        return type.__new__(cls, name, bases, dict(attrs, _meta=options))

    def __str__(cls):  # noqa: N802
        return cls._meta.name


class Scalar(six.with_metaclass(ScalarTypeMeta, UnmountedType)):
    '''
    Scalar Type Definition

    The leaf values of any request and input values to arguments are
    Scalars (or Enums) and are defined with a name and a series of functions
    used to parse input from ast or variables and to ensure validity.
    '''

    def __init__(self, *args, **kwargs):
        super(Scalar, self).__init__(*args, **kwargs)

        def get_type(self):
            return self
        self.get_type = types.MethodType(get_type, self)

    serialize = None
    parse_value = None
    parse_literal = None

    @classmethod
    def get_type(cls):
        return cls

# As per the GraphQL Spec, Integers are only treated as valid when a valid
# 32-bit signed integer, providing the broadest support across platforms.
#
# n.b. JavaScript's integers are safe between -(2^53 - 1) and 2^53 - 1 because
# they are internally represented as IEEE 754 doubles.
MAX_INT = 2147483647
MIN_INT = -2147483648


class Int(Scalar):
    '''
    The `Int` scalar type represents non-fractional signed whole numeric
    values. Int can represent values between -(2^53 - 1) and 2^53 - 1 since
    represented in JSON as double-precision floating point numbers specified
    by [IEEE 754](http://en.wikipedia.org/wiki/IEEE_floating_point).
    '''

    @staticmethod
    def coerce_int(value):
        try:
            num = int(value)
        except ValueError:
            try:
                num = int(float(value))
            except ValueError:
                return None
        if MIN_INT <= num <= MAX_INT:
            return num

    serialize = coerce_int
    parse_value = coerce_int

    @staticmethod
    def parse_literal(ast):
        if isinstance(ast, IntValue):
            num = int(ast.value)
            if MIN_INT <= num <= MAX_INT:
                return num


class Float(Scalar):
    '''
    The `Float` scalar type represents signed double-precision fractional
    values as specified by
    [IEEE 754](http://en.wikipedia.org/wiki/IEEE_floating_point).
    '''

    @staticmethod
    def coerce_float(value):
        try:
            return float(value)
        except ValueError:
            return None

    serialize = coerce_float
    parse_value = coerce_float

    @staticmethod
    def parse_literal(ast):
        if isinstance(ast, (FloatValue, IntValue)):
            return float(ast.value)


class String(Scalar):
    '''
    The `String` scalar type represents textual data, represented as UTF-8
    character sequences. The String type is most often used by GraphQL to
    represent free-form human-readable text.
    '''

    @staticmethod
    def coerce_string(value):
        if isinstance(value, bool):
            return u'true' if value else u'false'
        return six.text_type(value)

    serialize = coerce_string
    parse_value = coerce_string

    @staticmethod
    def parse_literal(ast):
        if isinstance(ast, StringValue):
            return ast.value


class Boolean(Scalar):
    '''
    The `Boolean` scalar type represents `true` or `false`.
    '''

    serialize = bool
    parse_value = bool

    @staticmethod
    def parse_literal(ast):
        if isinstance(ast, BooleanValue):
            return ast.value


class ID(Scalar):
    '''
    The `ID` scalar type represents a unique identifier, often used to
    refetch an object or as key for a cache. The ID type appears in a JSON
    response as a String; however, it is not intended to be human-readable.
    When expected as an input type, any string (such as `"4"`) or integer
    (such as `4`) input value will be accepted as an ID.
    '''

    serialize = str
    parse_value = str

    @staticmethod
    def parse_literal(ast):
        if isinstance(ast, (StringValue, IntValue)):
            return ast.value
