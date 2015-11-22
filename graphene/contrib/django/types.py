import six

from ...core.types import BaseObjectType, ObjectTypeMeta
from ...relay.fields import GlobalIDField
from ...relay.types import BaseNode, Connection
from .converter import convert_django_field
from .options import DjangoOptions
from .utils import get_reverse_fields, maybe_queryset


class DjangoObjectTypeMeta(ObjectTypeMeta):
    options_cls = DjangoOptions

    def is_interface(cls, parents):
        return DjangoInterface in parents

    def add_extra_fields(cls):
        if not cls._meta.model:
            return
        only_fields = cls._meta.only_fields
        reverse_fields = get_reverse_fields(cls._meta.model)
        all_fields = sorted(list(cls._meta.model._meta.fields) +
                            list(cls._meta.model._meta.local_many_to_many))
        all_fields += list(reverse_fields)
        already_created_fields = {f.attname for f in cls._meta.local_fields}

        for field in all_fields:
            is_not_in_only = only_fields and field.name not in only_fields
            is_already_created = field.name in already_created_fields
            is_excluded = field.name in cls._meta.exclude_fields or is_already_created
            if is_not_in_only or is_excluded:
                # We skip this field if we specify only_fields and is not
                # in there. Or when we exclude this field in exclude_fields
                continue
            converted_field = convert_django_field(field)
            cls.add_to_class(field.name, converted_field)


class InstanceObjectType(BaseObjectType):

    def __init__(self, _root=None):
        if _root:
            assert isinstance(_root, self._meta.model), (
                '{} received a non-compatible instance ({}) '
                'when expecting {}'.format(
                    self.__class__.__name__,
                    _root.__class__.__name__,
                    self._meta.model.__name__
                ))
        super(InstanceObjectType, self).__init__(_root=_root)

    @property
    def instance(self):
        return self._root

    @instance.setter
    def instance(self, value):
        self._root = value

    def __getattr__(self, attr):
        return getattr(self._root, attr)


class DjangoObjectType(six.with_metaclass(
        DjangoObjectTypeMeta, InstanceObjectType)):
    pass


class DjangoInterface(six.with_metaclass(
        DjangoObjectTypeMeta, InstanceObjectType)):
    pass


class DjangoConnection(Connection):

    @classmethod
    def from_list(cls, iterable, *args, **kwargs):
        iterable = maybe_queryset(iterable)
        return super(DjangoConnection, cls).from_list(iterable, *args, **kwargs)


class DjangoNode(BaseNode, DjangoInterface):
    id = GlobalIDField()

    @classmethod
    def get_node(cls, id, info=None):
        try:
            instance = cls._meta.model.objects.get(id=id)
            return cls(instance)
        except cls._meta.model.DoesNotExist:
            return None

    connection_type = DjangoConnection
