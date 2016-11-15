from ..unmountedtype import UnmountedType


class MyUnmountedType(UnmountedType):
    @classmethod
    def get_type(cls):
        '''
        This function is called when the unmounted type (Scalar instance)
        is mounted (as a Field, InputField or Argument)
        '''
        return cls


def test_unmountedtype_allows_setting_of_metadata():
    one = UnmountedType(_metadata='Test')

    assert one.metadata == 'Test'


def test_unmountedtype_metadata_defaults_to_none():
    one = UnmountedType()

    assert one.metadata is None


def test_unmountedtype_passes_on_metadata_to_field():
    one = MyUnmountedType(_metadata='Other Test')
    one_field = one.Field()

    assert one_field.metadata == 'Other Test'


def test_unmountedtype_passes_on_metadata_to_input_field():
    one = MyUnmountedType(_metadata='Other Test')
    one_input_field = one.InputField()

    assert one_input_field.metadata == 'Other Test'


def test_unmountedtype_passes_on_metadata_to_argument():
    one = MyUnmountedType(_metadata='Other Test')
    one_argument = one.Argument()

    assert one_argument.metadata == 'Other Test'
