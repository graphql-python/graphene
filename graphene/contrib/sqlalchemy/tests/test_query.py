import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

import graphene
from graphene import relay
from graphene.contrib.sqlalchemy import (SQLAlchemyConnectionField,
                                         SQLAlchemyNode, SQLAlchemyObjectType)

from .models import Article, Base, Editor, Reporter

db = create_engine('sqlite:///test_sqlalchemy.sqlite3')


@pytest.yield_fixture(scope='function')
def session():
    connection = db.engine.connect()
    transaction = connection.begin()
    Base.metadata.create_all(connection)

    # options = dict(bind=connection, binds={})
    session_factory = sessionmaker(bind=connection)
    session = scoped_session(session_factory)

    yield session

    # Finalize test here
    transaction.rollback()
    connection.close()
    session.remove()


def setup_fixtures(session):
    reporter = Reporter(first_name='ABA', last_name='X')
    session.add(reporter)
    reporter2 = Reporter(first_name='ABO', last_name='Y')
    session.add(reporter2)
    article = Article(headline='Hi!')
    session.add(article)
    editor = Editor(name="John")
    session.add(editor)
    session.commit()


def test_should_query_well(session):
    setup_fixtures(session)

    class ReporterType(SQLAlchemyObjectType):

        class Meta:
            model = Reporter

    class Query(graphene.ObjectType):
        reporter = graphene.Field(ReporterType)
        reporters = ReporterType.List()

        def resolve_reporter(self, *args, **kwargs):
            return session.query(Reporter).first()

        def resolve_reporters(self, *args, **kwargs):
            return session.query(Reporter)

    query = '''
        query ReporterQuery {
          reporter {
            firstName,
            lastName,
            email
          }
          reporters {
            firstName
          }
        }
    '''
    expected = {
        'reporter': {
            'firstName': 'ABA',
            'lastName': 'X',
            'email': None
        },
        'reporters': [{
            'firstName': 'ABA',
        }, {
            'firstName': 'ABO',
        }]
    }
    schema = graphene.Schema(query=Query)
    result = schema.execute(query)
    assert not result.errors
    assert result.data == expected


def test_should_node(session):
    setup_fixtures(session)

    class ReporterNode(SQLAlchemyNode):

        class Meta:
            model = Reporter

        @classmethod
        def get_node(cls, id, info):
            return Reporter(id=2, first_name='Cookie Monster')

        def resolve_articles(self, *args, **kwargs):
            return [Article(headline='Hi!')]

    class ArticleNode(SQLAlchemyNode):

        class Meta:
            model = Article

        # @classmethod
        # def get_node(cls, id, info):
        #     return Article(id=1, headline='Article node')

    class Query(graphene.ObjectType):
        node = relay.NodeField()
        reporter = graphene.Field(ReporterNode)
        article = graphene.Field(ArticleNode)
        all_articles = SQLAlchemyConnectionField(ArticleNode)

        def resolve_reporter(self, *args, **kwargs):
            return Reporter(id=1, first_name='ABA', last_name='X')

        def resolve_article(self, *args, **kwargs):
            return Article(id=1, headline='Article node')

    query = '''
        query ReporterQuery {
          reporter {
            id,
            firstName,
            articles {
              edges {
                node {
                  headline
                }
              }
            }
            lastName,
            email
          }
          allArticles {
            edges {
              node {
                headline
              }
            }
          }
          myArticle: node(id:"QXJ0aWNsZU5vZGU6MQ==") {
            id
            ... on ReporterNode {
                firstName
            }
            ... on ArticleNode {
                headline
            }
          }
        }
    '''
    expected = {
        'reporter': {
            'id': 'UmVwb3J0ZXJOb2RlOjE=',
            'firstName': 'ABA',
            'lastName': 'X',
            'email': None,
            'articles': {
                'edges': [{
                  'node': {
                      'headline': 'Hi!'
                  }
                }]
            },
        },
        'allArticles': {
            'edges': [{
                'node': {
                    'headline': 'Hi!'
                }
            }]
        },
        'myArticle': {
            'id': 'QXJ0aWNsZU5vZGU6MQ==',
            'headline': 'Hi!'
        }
    }
    schema = graphene.Schema(query=Query, session=session)
    result = schema.execute(query)
    assert not result.errors
    assert result.data == expected


def test_should_custom_identifier(session):
    setup_fixtures(session)

    class EditorNode(SQLAlchemyNode):

        class Meta:
            model = Editor
            identifier = "editor_id"

    class Query(graphene.ObjectType):
        node = relay.NodeField(EditorNode)
        all_editors = SQLAlchemyConnectionField(EditorNode)

    query = '''
        query EditorQuery {
          allEditors {
            edges {
                node {
                    id,
                    name
                }
            }
          },
          node(id: "RWRpdG9yTm9kZTox") {
            name
          }
        }
    '''
    expected = {
        'allEditors': {
            'edges': [{
                'node': {
                    'id': 'RWRpdG9yTm9kZTox',
                    'name': 'John'
                }
            }]
        },
        'node': {
            'name': 'John'
        }
    }

    schema = graphene.Schema(query=Query, session=session)
    result = schema.execute(query)
    assert not result.errors
    assert result.data == expected
