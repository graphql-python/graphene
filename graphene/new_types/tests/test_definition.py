from collections import OrderedDict

from py.test import raises

from ..objecttype import ObjectType
from ..scalars import String, Int, Boolean
from ..field import Field
from ..structures import List

from ..schema import Schema


class Image(ObjectType):
    url = String()
    width = Int()
    height = Int()


class Author(ObjectType):
    id = String()
    name = String()
    pic = Field(Image)  # width=Int(), height=Int()
    recent_article = Field(lambda: Article)


class Article(ObjectType):
    id = String()
    is_published = Boolean()
    author = Field(Author)
    title = String()
    body = String()


class Query(ObjectType):
    article = Field(Article)  # id=String()
    feed = List(Article)


class Mutation(ObjectType):
    write_article = Field(Article)


class Subscription(ObjectType):
    article_subscribe = Field(Article)  # id=String()


def test_defines_a_query_only_schema():
    blog_schema = Schema(Query)

    assert blog_schema.get_query_type() == Query

    article_field = Query._meta.fields['article']
    assert article_field.type == Article
    assert article_field.type._meta.name == 'Article'

    article_field_type = article_field.type
    assert issubclass(article_field_type, ObjectType)

    title_field = article_field_type._meta.fields['title']
    assert title_field.type == String

    author_field = article_field_type._meta.fields['author']
    author_field_type = author_field.type
    assert issubclass(author_field_type, ObjectType)
    recent_article_field = author_field_type._meta.fields['recent_article']

    assert recent_article_field.type() == Article

    feed_field = Query._meta.fields['feed']
    assert feed_field.type.of_type == Article
