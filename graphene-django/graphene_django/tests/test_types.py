from graphql.type import GraphQLObjectType
from mock import patch

from graphene import ObjectType, Field, Int, ID, Schema, Interface
from graphene.relay import Node, ConnectionField
from ..types import DjangoObjectType

from .models import Article as ArticleModel, Reporter as ReporterModel
from ..registry import reset_global_registry, Registry

reset_global_registry()


class Reporter(DjangoObjectType):
    '''Reporter description'''
    class Meta:
        model = ReporterModel


class Article(DjangoObjectType):
    '''Article description'''
    class Meta:
        model = ArticleModel
        interfaces = (Node, )


class RootQuery(ObjectType):
    node = Node.Field()


schema = Schema(query=RootQuery, types=[Article, Reporter])


def test_django_interface():
    assert issubclass(Node, Interface)
    assert issubclass(Node, Node)


@patch('graphene_django.tests.models.Article.objects.get', return_value=Article(id=1))
def test_django_get_node(get):
    article = Article.get_node(1, None, None)
    get.assert_called_with(id=1)
    assert article.id == 1


def test_django_objecttype_map_correct_fields():
    fields = Reporter._meta.fields
    assert list(fields.keys()) == ['id', 'first_name', 'last_name', 'email', 'pets', 'a_choice', 'articles', 'films']


def test_django_objecttype_with_node_have_correct_fields():
    fields = Article._meta.fields
    assert list(fields.keys()) == ['id', 'headline', 'pub_date', 'reporter', 'lang', 'importance']


def test_schema_representation():
    expected = """
schema {
  query: RootQuery
}

type Article implements Node {
  id: ID!
  headline: String
  pubDate: DateTime
  reporter: Reporter
  lang: ArticleLang
  importance: ArticleImportance
}

type ArticleConnection {
  pageInfo: PageInfo!
  edges: [ArticleEdge]
}

type ArticleEdge {
  node: Article
  cursor: String!
}

enum ArticleImportance {
  VERY_IMPORTANT
  NOT_AS_IMPORTANT
}

enum ArticleLang {
  SPANISH
  ENGLISH
}

scalar DateTime

interface Node {
  id: ID!
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}

type Reporter {
  id: ID
  firstName: String
  lastName: String
  email: String
  pets: [Reporter]
  aChoice: ReporterA_choice
  articles(before: String, after: String, first: Int, last: Int): ArticleConnection
}

enum ReporterA_choice {
  THIS
  THAT
}

type RootQuery {
  node(id: ID!): Node
}
""".lstrip()
    assert str(schema) == expected
