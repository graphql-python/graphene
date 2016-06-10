import six

from graphql import GraphQLInterfaceType
from .definitions import FieldsMeta, ClassTypeMeta, GrapheneGraphQLType


class GrapheneInterfaceType(GrapheneGraphQLType, GraphQLInterfaceType):
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

    def construct(cls, bases, attrs):
        if not cls._meta.abstract:
            local_fields = cls._extract_local_fields(attrs)
            if not cls._meta.graphql_type:
                cls._meta.graphql_type = GrapheneInterfaceType(
                    graphene_type=cls,
                    name=cls._meta.name or cls.__name__,
                    description=cls._meta.description or cls.__doc__,
                    fields=cls._fields(bases, attrs, local_fields),
                )
            else:
                assert not local_fields, "Can't mount Fields in an Interface with a defined graphql_type"

        return super(InterfaceTypeMeta, cls).construct(bases, attrs)


class Interface(six.with_metaclass(InterfaceTypeMeta)):
    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        from .objecttype import ObjectType
        if not isinstance(self, ObjectType):
            raise Exception("An interface cannot be intitialized")
        super(Interface, self).__init__(*args, **kwargs)

    @classmethod
    def implements(cls, object_type):
        '''
        We use this function for customizing when a ObjectType have this class as Interface
        For example, if we want to check that the ObjectType have some required things
        in it like Node.get_node
        '''
        pass
