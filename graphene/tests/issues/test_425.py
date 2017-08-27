# https://github.com/graphql-python/graphene/issues/425
# Adapted for Graphene 2.0

from graphene.types.objecttype import ObjectType, ObjectTypeOptions


class SpecialOptions(ObjectTypeOptions):
    other_attr = None


class SpecialObjectType(ObjectType):

    @classmethod
    def __init_subclass_with_meta__(cls, other_attr='default', **options):
        _meta = SpecialOptions(cls)
        _meta.other_attr = other_attr
        super(SpecialObjectType, cls).__init_subclass_with_meta__(_meta=_meta, **options)


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
    assert MyType._meta.default_resolver is None
    assert MyType._meta.interfaces == ()
