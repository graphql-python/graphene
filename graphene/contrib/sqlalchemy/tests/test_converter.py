from py.test import raises
from sqlalchemy import Column, Table, types
from sqlalchemy.orm import composite
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils.types.choice import ChoiceType
from sqlalchemy.dialects import postgresql

import graphene
from graphene.core.types.custom_scalars import JSONString
from graphene.contrib.sqlalchemy.converter import (convert_sqlalchemy_column,
                                                   convert_sqlalchemy_composite,
                                                   convert_sqlalchemy_relationship)
from graphene.contrib.sqlalchemy.fields import (ConnectionOrListField,
                                                SQLAlchemyModelField)

from .models import Article, Pet, Reporter


def assert_column_conversion(sqlalchemy_type, graphene_field, **kwargs):
    column = Column(sqlalchemy_type, doc='Custom Help Text', **kwargs)
    graphene_type = convert_sqlalchemy_column(column)
    assert isinstance(graphene_type, graphene_field)
    field = graphene_type.as_field()
    assert field.description == 'Custom Help Text'
    return field


def assert_composite_conversion(composite_class, composite_columns, graphene_field,
                                **kwargs):
    composite_column = composite(composite_class, *composite_columns,
                                 doc='Custom Help Text', **kwargs)
    graphene_type = convert_sqlalchemy_composite(composite_column)
    assert isinstance(graphene_type, graphene_field)
    field = graphene_type.as_field()
    # SQLAlchemy currently does not persist the doc onto the column, even though
    # the documentation says it does....
    # assert field.description == 'Custom Help Text'
    return field


def test_should_unknown_sqlalchemy_field_raise_exception():
    with raises(Exception) as excinfo:
        convert_sqlalchemy_column(None)
    assert 'Don\'t know how to convert the SQLAlchemy field' in str(excinfo.value)


def test_should_date_convert_string():
    assert_column_conversion(types.Date(), graphene.String)


def test_should_datetime_convert_string():
    assert_column_conversion(types.DateTime(), graphene.String)


def test_should_time_convert_string():
    assert_column_conversion(types.Time(), graphene.String)


def test_should_string_convert_string():
    assert_column_conversion(types.String(), graphene.String)


def test_should_text_convert_string():
    assert_column_conversion(types.Text(), graphene.String)


def test_should_unicode_convert_string():
    assert_column_conversion(types.Unicode(), graphene.String)


def test_should_unicodetext_convert_string():
    assert_column_conversion(types.UnicodeText(), graphene.String)


def test_should_enum_convert_string():
    assert_column_conversion(types.Enum(), graphene.String)


def test_should_small_integer_convert_int():
    assert_column_conversion(types.SmallInteger(), graphene.Int)


def test_should_big_integer_convert_int():
    assert_column_conversion(types.BigInteger(), graphene.Int)


def test_should_integer_convert_int():
    assert_column_conversion(types.Integer(), graphene.Int)


def test_should_integer_convert_id():
    assert_column_conversion(types.Integer(), graphene.ID, primary_key=True)


def test_should_boolean_convert_boolean():
    assert_column_conversion(types.Boolean(), graphene.Boolean)


def test_should_float_convert_float():
    assert_column_conversion(types.Float(), graphene.Float)


def test_should_numeric_convert_float():
    assert_column_conversion(types.Numeric(), graphene.Float)


def test_should_choice_convert_enum():
    TYPES = [
        (u'es', u'Spanish'),
        (u'en', u'English')
    ]
    column = Column(ChoiceType(TYPES), doc='Language', name='language')
    Base = declarative_base()

    Table('translatedmodel', Base.metadata, column)
    graphene_type = convert_sqlalchemy_column(column)
    assert issubclass(graphene_type, graphene.Enum)
    assert graphene_type._meta.type_name == 'TRANSLATEDMODEL_LANGUAGE'
    assert graphene_type._meta.description == 'Language'
    assert graphene_type.__enum__.__members__['es'].value == 'Spanish'
    assert graphene_type.__enum__.__members__['en'].value == 'English'


def test_should_manytomany_convert_connectionorlist():
    graphene_type = convert_sqlalchemy_relationship(Reporter.pets.property)
    assert isinstance(graphene_type, ConnectionOrListField)
    assert isinstance(graphene_type.type, SQLAlchemyModelField)
    assert graphene_type.type.model == Pet


def test_should_manytoone_convert_connectionorlist():
    field = convert_sqlalchemy_relationship(Article.reporter.property)
    assert isinstance(field, SQLAlchemyModelField)
    assert field.model == Reporter


def test_should_onetomany_convert_model():
    graphene_type = convert_sqlalchemy_relationship(Reporter.articles.property)
    assert isinstance(graphene_type, ConnectionOrListField)
    assert isinstance(graphene_type.type, SQLAlchemyModelField)
    assert graphene_type.type.model == Article


def test_should_postgresql_uuid_convert():
    assert_column_conversion(postgresql.UUID(), graphene.String)


def test_should_postgresql_enum_convert():
    assert_column_conversion(postgresql.ENUM(), graphene.String)


def test_should_postgresql_array_convert():
    assert_column_conversion(postgresql.ARRAY(types.Integer), graphene.List)


def test_should_postgresql_json_convert():
    assert_column_conversion(postgresql.JSON(), JSONString)


def test_should_postgresql_jsonb_convert():
    assert_column_conversion(postgresql.JSONB(), JSONString)


def test_should_postgresql_hstore_convert():
    assert_column_conversion(postgresql.HSTORE(), JSONString)


def test_should_composite_convert():

    class CompositeClass(object):
        def __init__(self, col1, col2):
            self.col1 = col1
            self.col2 = col2

    @convert_sqlalchemy_composite.register(CompositeClass)
    def convert_composite_class(composite):
        return graphene.String(description=composite.doc)

    assert_composite_conversion(CompositeClass,
                                (Column(types.Unicode(50)),
                                 Column(types.Unicode(50))),
                                graphene.String)


def test_should_unknown_sqlalchemy_composite_raise_exception():
    with raises(Exception) as excinfo:

        class CompositeClass(object):
            def __init__(self, col1, col2):
                self.col1 = col1
                self.col2 = col2

        assert_composite_conversion(CompositeClass,
                                    (Column(types.Unicode(50)),
                                     Column(types.Unicode(50))),
                                    graphene.String)

    assert 'Don\'t know how to convert the composite field' in str(excinfo.value)
