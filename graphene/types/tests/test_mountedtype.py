import pytest

from ..mountedtype import MountedType
from ..field import Field
from ..objecttype import ObjectType
from ..scalars import String


class CustomField(Field):
    def __init__(self, *args, **kwargs):
        self.metadata = kwargs.pop('metadata', None)
        super(CustomField, self).__init__(*args, **kwargs)


def test_mounted_type():
    unmounted = String()
    mounted = Field.mount(unmounted)
    assert isinstance(mounted, Field)
    assert mounted.type == String


def test_mounted_type_custom():
    unmounted = String(metadata={'hey': 'yo!'})
    mounted = CustomField.mount(unmounted)
    assert isinstance(mounted, CustomField)
    assert mounted.type == String
    assert mounted.metadata == {'hey': 'yo!'}


@pytest.yield_fixture
def custom_field():
    # We set the override
    Field._mount_cls_override = CustomField

    # Run the test
    yield CustomField

    # Remove the class override (back to the original state)
    Field._mount_cls_override = None


def test_mounted_type_overrided(custom_field):
    # This function is using the custom_field yield fixture

    unmounted = String(metadata={'hey': 'yo!'})
    mounted = Field.mount(unmounted)
    assert isinstance(mounted, CustomField)
    assert mounted.type == String
    assert mounted.metadata == {'hey': 'yo!'}


def test_mounted_type_overrided(custom_field):
    # This function is using the custom_field yield fixture

    class Query(ObjectType):
        test = String(metadata={'other': 'thing'})

    test_field = Query._meta.fields['test']
    assert isinstance(test_field, CustomField)
    assert test_field.metadata == {'other': 'thing'}
