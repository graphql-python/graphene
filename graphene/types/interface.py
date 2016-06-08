from itertools import chain
from functools import partial
from collections import OrderedDict
import six

from graphql import GraphQLInterfaceType
from .definitions import ClassTypeMeta, GrapheneFieldsType, FieldMap


class GrapheneInterfaceType(GrapheneFieldsType, GraphQLInterfaceType):
    pass


class InterfaceTypeMeta(ClassTypeMeta):

    def get_options(cls, meta):
        return cls.options_class(
            meta,
            name=None,
            description=None,
            graphql_type=None,
            abstract=False
        )

    def construct_graphql_type(cls, bases):
        pass

    def _build_field_map(cls, local_fields, bases):
        from ..utils.extract_fields import get_base_fields
        extended_fields = get_base_fields(bases)
        fields = chain(extended_fields, local_fields)
        return OrderedDict((f.name, f) for f in fields)

    def construct(cls, bases, attrs):
        if not cls._meta.graphql_type and not cls._meta.abstract:
            from ..utils.is_graphene_type import is_graphene_type
            from ..utils.extract_fields import extract_fields

            inherited_types = [
                base._meta.graphql_type for base in bases if is_graphene_type(base)
            ]
            inherited_types = filter(None, inherited_types)

            local_fields = list(extract_fields(attrs))

            cls._meta.graphql_type = GrapheneInterfaceType(
                graphene_type=cls,
                name=cls._meta.name or cls.__name__,
                description=cls._meta.description or cls.__doc__,
                fields=partial(cls._build_field_map, local_fields, inherited_types),
            )
        return super(InterfaceTypeMeta, cls).construct(bases, attrs)


class Interface(six.with_metaclass(InterfaceTypeMeta)):
    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        raise Exception("An interface cannot be intitialized")

    @classmethod
    def implements(cls, object_type):
        '''
        We use this function for customizing when a ObjectType have this class as Interface
        For example, if we want to check that the ObjectType have some required things
        in it like Node.get_node
        '''
        pass
