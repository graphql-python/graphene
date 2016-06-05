import six
from graphql import GraphQLScalarType, GraphQLString, GraphQLInt, GraphQLFloat, GraphQLBoolean, GraphQLID

from .definitions import ClassTypeMeta, GrapheneType
from .proxy import TypeProxy


class GrapheneScalarType(GrapheneType, GraphQLScalarType):

    def __init__(self, *args, **kwargs):
        GrapheneType.__init__(self, *args, **kwargs)

    @staticmethod
    def default_parse(value):
        return None

    def setup(self):
        serialize = getattr(self.graphene_type, 'serialize', None)
        parse_value = getattr(self.graphene_type, 'parse_value', None)
        parse_literal = getattr(self.graphene_type, 'parse_literal', None)

        assert callable(serialize), (
            '{} must provide "serialize" function. If this custom Scalar is '
            'also used as an input type, ensure "parse_value" and "parse_literal" '
            'functions are also provided.'
        ).format(self)

        if parse_value is not None or parse_literal is not None:
            assert callable(parse_value) and callable(parse_literal), (
                '{} must provide both "parse_value" and "parse_literal" functions.'.format(self)
            )

        self._serialize = serialize
        self._parse_value = parse_value
        self._parse_literal = parse_literal

    @property
    def serialize(self):
        return self.graphene_type.serialize

    @property
    def parse_value(self):
        return getattr(self.graphene_type, 'parse_value', self.default_parse)

    @property
    def parse_literal(self):
        return getattr(self.graphene_type, 'parse_literal', self.default_parse)


class ScalarTypeMeta(ClassTypeMeta):

    def get_options(cls, meta):
        return cls.options_class(
            meta,
            name=None,
            description=None,
            graphql_type=None,
            abstract=False
        )

    def construct_graphql_type(cls, bases):
        if not cls._meta.graphql_type and not cls._meta.abstract:
            cls._meta.graphql_type = GrapheneScalarType(
                graphene_type=cls,
                name=cls._meta.name or cls.__name__,
                description=cls._meta.description,
                # For passing the assertion in GraphQLScalarType
                serialize=lambda: None
            )

    def construct(cls, *args, **kwargs):
        constructed = super(ScalarTypeMeta, cls).construct(*args, **kwargs)
        if isinstance(cls._meta.graphql_type, GrapheneScalarType):
            cls._meta.graphql_type.setup()
        return constructed


class Scalar(six.with_metaclass(ScalarTypeMeta, TypeProxy)):
    class Meta:
        abstract = True


def construct_scalar_class(graphql_type):
    # This is equivalent to
    # class String(Scalar):
    #     class Meta:
    #         graphql_type = graphql_type
    Meta = type('Meta', (object,), {'graphql_type':graphql_type})
    return type(graphql_type.name, (Scalar, ), {'Meta': Meta})


String = construct_scalar_class(GraphQLString)
Int = construct_scalar_class(GraphQLInt)
Float = construct_scalar_class(GraphQLFloat)
Boolean = construct_scalar_class(GraphQLBoolean)
ID = construct_scalar_class(GraphQLID)
