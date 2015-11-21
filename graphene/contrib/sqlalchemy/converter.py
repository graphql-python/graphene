from sqlalchemy import types
from sqlalchemy.orm import interfaces
from singledispatch import singledispatch

from graphene.contrib.sqlalchemy.fields import ConnectionOrListField, SQLAlchemyModelField
from graphene.core.fields import BooleanField, FloatField, IDField, IntField, StringField


def convert_sqlalchemy_relationship(relationship):
    model_field = SQLAlchemyModelField(field.table, description=relationship.key)
    if relationship.direction == interfaces.ONETOMANY:
        return model_field
    elif (relationship.direction == interfaces.MANYTOONE or
          relationship.direction == interfaces.MANYTOMANY):
        return ConnectionOrListField(model_field)


def convert_sqlalchemy_column(column):
    try:
        return convert_sqlalchemy_type(column.type, column)
    except Exception:
        raise


@singledispatch
def convert_sqlalchemy_type():
    raise Exception(
        "Don't know how to convert the SQLAlchemy column %s (%s)" % (column, column.__class__))


@convert_sqlalchemy_type.register(types.Date)
@convert_sqlalchemy_type.register(types.DateTime)
@convert_sqlalchemy_type.register(types.Time)
@convert_sqlalchemy_type.register(types.Text)
@convert_sqlalchemy_type.register(types.String)
@convert_sqlalchemy_type.register(types.Unicode)
@convert_sqlalchemy_type.register(types.UnicodeText)
@convert_sqlalchemy_type.register(types.Enum)
def convert_column_to_string(type, column):
    return StringField(description=column.description)


@convert_sqlalchemy_type.register(types.SmallInteger)
@convert_sqlalchemy_type.register(types.BigInteger)
@convert_sqlalchemy_type.register(types.Integer)
def convert_column_to_int_or_id(column):
    if column.primary_key:
        return IDField(description=column.description)
    else:
        return IntField(description=column.description)


@convert_sqlalchemy_type.register(types.Boolean)
def convert_column_to_boolean(column):
    return BooleanField(description=column.description)


@convert_sqlalchemy_type.register(types.Float)
@convert_sqlalchemy_type.register(types.Numeric)
def convert_column_to_float(column):
    return FloatField(description=column.description)
