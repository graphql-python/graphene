from singledispatch import singledispatch
from sqlalchemy import types
from sqlalchemy.orm import interfaces
from sqlalchemy.dialects import postgresql

from graphene import Enum, ID, Boolean, Float, Int, String, List, Field
from graphene.relay import Node
from graphene.types.json import JSONString
from .fields import SQLAlchemyConnectionField

try:
    from sqlalchemy_utils.types.choice import ChoiceType
except ImportError:
    class ChoiceType(object):
        pass


def convert_sqlalchemy_relationship(relationship, registry):
    direction = relationship.direction
    model = relationship.mapper.entity
    _type = registry.get_type_for_model(model)
    if not _type:
        return None
    if direction == interfaces.MANYTOONE:
        return Field(_type)
    elif (direction == interfaces.ONETOMANY or
          direction == interfaces.MANYTOMANY):
        if issubclass(_type, Node):
            return SQLAlchemyConnectionField(_type)
        return List(_type)


def convert_sqlalchemy_column(column, registry=None):
    return convert_sqlalchemy_type(getattr(column, 'type', None), column, registry)


@singledispatch
def convert_sqlalchemy_type(type, column, registry=None):
    raise Exception(
        "Don't know how to convert the SQLAlchemy field %s (%s)" % (column, column.__class__))


@convert_sqlalchemy_type.register(types.Date)
@convert_sqlalchemy_type.register(types.DateTime)
@convert_sqlalchemy_type.register(types.Time)
@convert_sqlalchemy_type.register(types.String)
@convert_sqlalchemy_type.register(types.Text)
@convert_sqlalchemy_type.register(types.Unicode)
@convert_sqlalchemy_type.register(types.UnicodeText)
@convert_sqlalchemy_type.register(types.Enum)
@convert_sqlalchemy_type.register(postgresql.ENUM)
@convert_sqlalchemy_type.register(postgresql.UUID)
def convert_column_to_string(type, column, registry=None):
    return String(description=column.doc)


@convert_sqlalchemy_type.register(types.SmallInteger)
@convert_sqlalchemy_type.register(types.BigInteger)
@convert_sqlalchemy_type.register(types.Integer)
def convert_column_to_int_or_id(type, column, registry=None):
    if column.primary_key:
        return ID(description=column.doc)
    else:
        return Int(description=column.doc)


@convert_sqlalchemy_type.register(types.Boolean)
def convert_column_to_boolean(type, column, registry=None):
    return Boolean(description=column.doc)


@convert_sqlalchemy_type.register(types.Float)
@convert_sqlalchemy_type.register(types.Numeric)
def convert_column_to_float(type, column, registry=None):
    return Float(description=column.doc)


@convert_sqlalchemy_type.register(ChoiceType)
def convert_column_to_enum(type, column, registry=None):
    name = '{}_{}'.format(column.table.name, column.name).upper()
    return Enum(name, type.choices, description=column.doc)


@convert_sqlalchemy_type.register(postgresql.ARRAY)
def convert_postgres_array_to_list(type, column, registry=None):
    graphene_type = convert_sqlalchemy_type(column.type.item_type, column)
    return List(graphene_type, description=column.doc)


@convert_sqlalchemy_type.register(postgresql.HSTORE)
@convert_sqlalchemy_type.register(postgresql.JSON)
@convert_sqlalchemy_type.register(postgresql.JSONB)
def convert_json_to_string(type, column, registry=None):
    return JSONString(description=column.doc)
