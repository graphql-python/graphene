import six

from .definitions import ClassTypeMeta, GrapheneInterfaceType, FieldMap


class InterfaceTypeMeta(ClassTypeMeta):

    def get_options(cls, meta):
        options = cls.options_class(
            meta,
            name=None,
            description=None,
            graphql_type=None,
        )
        options.valid_attrs = ['graphql_type', 'name', 'description', 'abstract']
        return options

    def construct_graphql_type(cls, bases):
        if not cls._meta.graphql_type and not cls._meta.abstract:
            from ..utils.is_graphene_type import is_graphene_type
            inherited_types = [
                base._meta.graphql_type for base in bases if is_graphene_type(base)
            ]

            cls._meta.graphql_type = GrapheneInterfaceType(
                graphene_type=cls,
                name=cls._meta.name or cls.__name__,
                description=cls._meta.description,
                fields=FieldMap(cls, bases=filter(None, inherited_types)),
            )


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
