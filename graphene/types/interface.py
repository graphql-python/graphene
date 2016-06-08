import six

from graphql import GraphQLInterfaceType
from .definitions import FieldsMeta, ClassTypeMeta, GrapheneFieldsType


class GrapheneInterfaceType(GrapheneFieldsType, GraphQLInterfaceType):
    pass


class InterfaceTypeMeta(FieldsMeta, ClassTypeMeta):

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

    def construct(cls, bases, attrs):
        if not cls._meta.graphql_type and not cls._meta.abstract:

            cls._meta.graphql_type = GrapheneInterfaceType(
                graphene_type=cls,
                name=cls._meta.name or cls.__name__,
                description=cls._meta.description or cls.__doc__,
                fields=cls._fields(bases, attrs),
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
