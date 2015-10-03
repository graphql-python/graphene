import json
import pytest
from py.test import raises
from collections import namedtuple
from pytest import raises
from graphene.core.fields import (
    Field,
    StringField,
)
from graphql.core.type import (
    GraphQLObjectType,
    GraphQLInterfaceType
)

from graphene import Schema
from graphene.contrib.django.types import (
    DjangoNode,
    DjangoInterface
)


def format_response(response):
    return json.loads(response.content)


def test_client_get_no_query(settings, client):
    settings.ROOT_URLCONF = 'tests.contrib_django.test_urls'
    response = client.get('/graphql')
    json_response = format_response(response)
    assert json_response == {'errors': [{'message': 'Must provide query string.'}]}


def test_client_post_no_query(settings, client):
    settings.ROOT_URLCONF = 'tests.contrib_django.test_urls'
    response = client.post('/graphql', {})
    print response.content
    json_response = format_response(response)
    assert json_response == {'errors': [{'message': 'Must provide query string.'}]}


def test_client_post_malformed_json(settings, client):
    settings.ROOT_URLCONF = 'tests.contrib_django.test_urls'
    response = client.post('/graphql', 'MALFORMED', 'application/json')
    json_response = format_response(response)
    assert json_response == {'errors': [{'message': 'Malformed json body in the post data'}]}


def test_client_post_empty_query(settings, client):
    settings.ROOT_URLCONF = 'tests.contrib_django.test_urls'
    response = client.post('/graphql', json.dumps({'query': ''}), 'application/json')
    json_response = format_response(response)
    assert json_response == {'errors': [{'message': 'Must provide query string.'}]}


def test_client_post_bad_query(settings, client):
    settings.ROOT_URLCONF = 'tests.contrib_django.test_urls'
    response = client.post('/graphql', json.dumps({'query': '{ MALFORMED'}), 'application/json')
    json_response = format_response(response)
    assert 'errors' in json_response
    assert len(json_response['errors']) == 1
    assert 'Syntax Error GraphQL' in json_response['errors'][0]['message']


def test_client_get_good_query(settings, client):
    settings.ROOT_URLCONF = 'tests.contrib_django.test_urls'
    response = client.get('/graphql', {'query': '{ headline }'})
    json_response = format_response(response)
    expected_json = {
        'data': {
            'headline': None
        }
    }
    assert json_response == expected_json


def test_client_post_good_query(settings, client):
    settings.ROOT_URLCONF = 'tests.contrib_django.test_urls'
    response = client.post('/graphql', json.dumps({'query': '{ headline }'}), 'application/json')
    json_response = format_response(response)
    expected_json = {
        'data': {
            'headline': None
        }
    }
    assert json_response == expected_json


# def test_client_get_bad_query(settings, client):
#     settings.ROOT_URLCONF = 'tests.contrib_django.test_urls'
#     response = client.get('/graphql')
#     json_response = format_response(response)
#     assert json_response == {'errors': [{'message': 'Must provide query string.'}]}


