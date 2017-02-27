# https://github.com/graphql-python/graphene/issues/425
import six

from graphene.utils.is_base_type import is_base_type

from graphene.types.objecttype import ObjectTypeMeta, ObjectType
from graphene.types.options import Options

class SpecialObjectTypeMeta(ObjectTypeMeta):

    @staticmethod
    def __new__(cls, name, bases, attrs):
        # Also ensure initialization is only performed for subclasses of
        # DjangoObjectType
        if not is_base_type(bases, SpecialObjectTypeMeta):
            return type.__new__(cls, name, bases, attrs)

        options = Options(
            attrs.pop('Meta', None),
            other_attr='default',
        )

        return ObjectTypeMeta.__new__(cls, name, bases, dict(attrs, _meta=options))

        return cls


class SpecialObjectType(six.with_metaclass(SpecialObjectTypeMeta, ObjectType)):
    pass


def test_special_objecttype_could_be_subclassed():
    class MyType(SpecialObjectType):
        class Meta:
            other_attr = 'yeah!'

    assert MyType._meta.other_attr == 'yeah!'


def test_special_objecttype_could_be_subclassed_default():
    class MyType(SpecialObjectType):
        pass

    assert MyType._meta.other_attr == 'default'


def test_special_objecttype_inherit_meta_options():
    class MyType(SpecialObjectType):
        pass

    assert MyType._meta.name == 'MyType'
    assert MyType._meta.default_resolver == None
    assert MyType._meta.interfaces == ()
