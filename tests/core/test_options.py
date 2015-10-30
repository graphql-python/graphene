from py.test import raises
from collections import namedtuple
from pytest import raises
from graphene.core.fields import (
    Field,
    StringField,
)

from graphene.core.options import Options


class Meta:
    is_interface = True
    type_name = 'Character'


class InvalidMeta:
    other_value = True


def test_field_added_in_meta():
    opt = Options(Meta)

    class ObjectType(object):
        pass

    opt.contribute_to_class(ObjectType, '_meta')
    f = StringField()
    f.field_name = 'string_field'
    opt.add_field(f)
    assert f in opt.fields


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
        pass

    opt.contribute_to_class(ObjectType, '_meta')
    assert opt.description == 'False description'


def test_field_no_contributed_raises_error():
    opt = Options(InvalidMeta)

    class ObjectType(object):
        pass

    with raises(Exception) as excinfo:
        opt.contribute_to_class(ObjectType, '_meta')

    assert 'invalid attribute' in str(excinfo.value)
