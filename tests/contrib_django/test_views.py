import json


def format_response(response):
    return json.loads(response.content.decode())


def test_client_get_no_query(settings, client):
    settings.ROOT_URLCONF = 'tests.contrib_django.test_urls'
    response = client.get('/graphql')
    json_response = format_response(response)
    assert json_response == {'errors': [
        {'message': 'Must provide query string.'}]}


def test_client_post_no_query(settings, client):
    settings.ROOT_URLCONF = 'tests.contrib_django.test_urls'
    response = client.post('/graphql', {})
    json_response = format_response(response)
    assert json_response == {'errors': [
        {'message': 'Must provide query string.'}]}


def test_client_post_malformed_json(settings, client):
    settings.ROOT_URLCONF = 'tests.contrib_django.test_urls'
    response = client.post('/graphql', 'MALFORMED', 'application/json')
    json_response = format_response(response)
    assert json_response == {'errors': [
        {'message': 'Malformed json body in the post data'}]}


def test_client_post_empty_query(settings, client):
    settings.ROOT_URLCONF = 'tests.contrib_django.test_urls'
    response = client.post(
        '/graphql', json.dumps({'query': ''}), 'application/json')
    json_response = format_response(response)
    assert json_response == {'errors': [
        {'message': 'Must provide query string.'}]}


def test_client_post_bad_query(settings, client):
    settings.ROOT_URLCONF = 'tests.contrib_django.test_urls'
    response = client.post(
        '/graphql', json.dumps({'query': '{ MALFORMED'}), 'application/json')
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


def test_client_get_good_query_with_raise(settings, client):
    settings.ROOT_URLCONF = 'tests.contrib_django.test_urls'
    response = client.get('/graphql', {'query': '{ raises }'})
    json_response = format_response(response)
    assert json_response['errors'][0][
        'message'] == 'This field should raise exception'
    assert json_response['data']['raises'] is None


def test_client_post_good_query(settings, client):
    settings.ROOT_URLCONF = 'tests.contrib_django.test_urls'
    response = client.post(
        '/graphql', json.dumps({'query': '{ headline }'}), 'application/json')
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
