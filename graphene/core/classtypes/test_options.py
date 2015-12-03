from py.test import raises

from graphene.core.classtypes import Options


class Meta:
    type_name = 'Character'


class InvalidMeta:
    other_value = True


def test_options_contribute():
    opt = Options(Meta)

    class ObjectType(object):
        pass

    opt.contribute_to_class(ObjectType, '_meta')
    assert ObjectType._meta == opt


def test_options_typename():
    opt = Options(Meta)

    class ObjectType(object):
        pass

    opt.contribute_to_class(ObjectType, '_meta')
    assert opt.type_name == 'Character'


def test_options_description():
    opt = Options(Meta)

    class ObjectType(object):

        '''False description'''

    opt.contribute_to_class(ObjectType, '_meta')
    assert opt.description == 'False description'


def test_field_no_contributed_raises_error():
    opt = Options(InvalidMeta)

    class ObjectType(object):
        pass

    with raises(Exception) as excinfo:
        opt.contribute_to_class(ObjectType, '_meta')

    assert 'invalid attribute' in str(excinfo.value)
