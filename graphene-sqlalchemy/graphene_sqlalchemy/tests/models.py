from __future__ import absolute_import

from sqlalchemy import Column, Date, ForeignKey, Integer, String, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

association_table = Table('association', Base.metadata,
                          Column('pet_id', Integer, ForeignKey('pets.id')),
                          Column('reporter_id', Integer, ForeignKey('reporters.id')))


class Editor(Base):
    __tablename__ = 'editors'
    editor_id = Column(Integer(), primary_key=True)
    name = Column(String(100))


class Pet(Base):
    __tablename__ = 'pets'
    id = Column(Integer(), primary_key=True)
    name = Column(String(30))
    reporter_id = Column(Integer(), ForeignKey('reporters.id'))


class Reporter(Base):
    __tablename__ = 'reporters'
    id = Column(Integer(), primary_key=True)
    first_name = Column(String(30))
    last_name = Column(String(30))
    email = Column(String())
    pets = relationship('Pet', secondary=association_table, backref='reporters')
    articles = relationship('Article', backref='reporter')


class Article(Base):
    __tablename__ = 'articles'
    id = Column(Integer(), primary_key=True)
    headline = Column(String(100))
    pub_date = Column(Date())
    reporter_id = Column(Integer(), ForeignKey('reporters.id'))
