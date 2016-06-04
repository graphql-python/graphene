from collections import OrderedDict
import inspect
import copy

from graphql.utils.assert_valid_name import assert_valid_name
from graphql.type.definition import GraphQLObjectType, GraphQLInterfaceType, GraphQLScalarType

from .options import Options


class ClassTypeMeta(type):
    options_class = Options

    def __new__(mcs, name, bases, attrs):
        super_new = super(ClassTypeMeta, mcs).__new__

        module = attrs.pop('__module__', None)
        doc = attrs.pop('__doc__', None)
        new_class = super_new(mcs, name, bases, {
            '__module__': module,
            '__doc__': doc
        })
        attr_meta = attrs.pop('Meta', None)
        if not attr_meta:
            meta = getattr(new_class, 'Meta', None)
        else:
            meta = attr_meta

        new_class.add_to_class('_meta', new_class.get_options(meta))
        if new_class._meta.name:
            assert_valid_name(new_class._meta.name)
        new_class.construct_graphql_type(bases)

        return mcs.construct(new_class, bases, attrs)

    def get_options(cls, meta):
        raise NotImplementedError("get_options is not implemented")

    def construct_graphql_type(cls, bases):
        raise NotImplementedError("construct_graphql_type is not implemented")

    def add_to_class(cls, name, value):
        # We should call the contribute_to_class method only if it's bound
        if not inspect.isclass(value) and hasattr(
                value, 'contribute_to_class'):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)

    def construct(cls, bases, attrs):
        # Add all attributes to the class.
        for obj_name, obj in attrs.items():
            cls.add_to_class(obj_name, obj)

        # if not cls._meta.abstract:
        #     from ..types import List, NonNull

        return cls


class GrapheneType(object):
    def __init__(self, *args, **kwargs):
        self.graphene_type = kwargs.pop('graphene_type')
        self._name = None
        self._description = None
        super(GrapheneType, self).__init__(*args, **kwargs)

    @property
    def name(self):
        return self._name or self.graphene_type.__name__

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def description(self):
        return self._description or self.graphene_type.__doc__

    @description.setter
    def description(self, description):
        self._description = description


class GrapheneFieldsType(GrapheneType):
    def __init__(self, *args, **kwargs):
        self._fields = None
        self._field_map = None
        super(GrapheneFieldsType, self).__init__(*args, **kwargs)

    def add_field(self, field):
        # We clear the cached fields
        self._field_map = None
        self._fields.add(field)


class FieldMap(object):
    def __init__(self, parent, bases=None, fields=None):
        self.parent = parent
        self.fields = fields or []
        self.bases = bases or []

    def add(self, field):
        self.fields.append(field)

    def __call__(self):
        # It's in a call function for assuring that if a field is added
        # in runtime then it will be reflected in the Class type fields
        # If we add the field in the class type creation, then we
        # would not be able to change it later.
        from .field import Field
        prev_fields = []
        graphql_type = self.parent._meta.graphql_type

        # We collect the fields from the interfaces
        if isinstance(graphql_type, GraphQLObjectType):
            interfaces = graphql_type.get_interfaces()
            for interface in interfaces:
                prev_fields += interface.get_fields().items()

        # We collect the fields from the bases
        for base in self.bases:
            prev_fields += base.get_fields().items()

        fields = prev_fields + [
            (field.name, field) for field in sorted(self.fields)
        ]

        # Then we copy all the fields and assign the parent
        new_fields = []
        for field_name, field in fields:
            field = copy.copy(field)
            if isinstance(field, Field):
                field.parent = self.parent
            new_fields.append((field_name, field))

        return OrderedDict(new_fields)


class GrapheneObjectType(GrapheneFieldsType, GraphQLObjectType):
    __slots__ = ('graphene_type', '_name', '_description', '_fields', '_field_map', '_is_type_of', '_provided_interfaces', '_interfaces')

    @property
    def is_type_of(self):
        return self._is_type_of or self.default_is_type_of

    @is_type_of.setter
    def is_type_of(self, is_type_of):
        self._is_type_of = is_type_of

    def default_is_type_of(self, interface, context, info):
        from ..utils.get_graphql_type import get_graphql_type
        try:
            graphql_type = get_graphql_type(type(interface))
            return graphql_type == self
        except:
            return False

    def add_interface(self, interface):
        from ..utils.get_graphql_type import get_graphql_type
        # We clear the cached interfaces
        self._interfaces = None
        # We clear the cached fields as could be inherited from interfaces
        self._field_map = None
        graphql_type = get_graphql_type(interface)

        if isinstance(graphql_type, GrapheneInterfaceType):
            graphql_type.graphene_type.implements(self.graphene_type)

        self._provided_interfaces.append(graphql_type)


class GrapheneInterfaceType(GrapheneFieldsType, GraphQLInterfaceType):
    __slots__ = ('graphene_type', '_name', '_description', '_fields', '_field_map', 'resolve_type')


class GrapheneScalarType(GrapheneType, GraphQLScalarType):
    __slots__ = ('graphene_type', '_name', '_description', '_serialize', '_parse_value', '_parse_literal')

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
