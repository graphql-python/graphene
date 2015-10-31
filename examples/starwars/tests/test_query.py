
from ..data import setup
from ..schema import Schema

setup()


def test_hero_name_query():
    query = '''
        query HeroNameQuery {
          hero {
            name
          }
        }
    '''
    expected = {
        'hero': {
            'name': 'R2-D2'
        }
    }
    result = Schema.execute(query)
    assert not result.errors
    assert result.data == expected


def test_hero_name_and_friends_query():
    query = '''
        query HeroNameAndFriendsQuery {
          hero {
            id
            name
            friends {
              name
            }
          }
        }
    '''
    expected = {
        'hero': {
            'id': '2001',
            'name': 'R2-D2',
            'friends': [
                {'name': 'Luke Skywalker'},
                {'name': 'Han Solo'},
                {'name': 'Leia Organa'},
            ]
        }
    }
    result = Schema.execute(query)
    assert not result.errors
    assert result.data == expected


def test_nested_query():
    query = '''
        query NestedQuery {
          hero {
            name
            friends {
              name
              appearsIn
              friends {
                name
              }
            }
          }
        }
    '''
    expected = {
        'hero': {
            'name': 'R2-D2',
            'friends': [
                {
                    'name': 'Luke Skywalker',
                    'appearsIn': ['NEWHOPE', 'EMPIRE', 'JEDI'],
                    'friends': [
                        {
                            'name': 'Han Solo',
                        },
                        {
                            'name': 'Leia Organa',
                        },
                        {
                            'name': 'C-3PO',
                        },
                        {
                            'name': 'R2-D2',
                        },
                    ]
                },
                {
                    'name': 'Han Solo',
                    'appearsIn': ['NEWHOPE', 'EMPIRE', 'JEDI'],
                    'friends': [
                        {
                            'name': 'Luke Skywalker',
                        },
                        {
                            'name': 'Leia Organa',
                        },
                        {
                            'name': 'R2-D2',
                        },
                    ]
                },
                {
                    'name': 'Leia Organa',
                    'appearsIn': ['NEWHOPE', 'EMPIRE', 'JEDI'],
                    'friends': [
                        {
                            'name': 'Luke Skywalker',
                        },
                        {
                            'name': 'Han Solo',
                        },
                        {
                            'name': 'C-3PO',
                        },
                        {
                            'name': 'R2-D2',
                        },
                    ]
                },
            ]
        }
    }
    result = Schema.execute(query)
    assert not result.errors
    assert result.data == expected


def test_fetch_luke_query():
    query = '''
        query FetchLukeQuery {
          human(id: "1000") {
            name
          }
        }
    '''
    expected = {
        'human': {
            'name': 'Luke Skywalker',
        }
    }
    result = Schema.execute(query)
    assert not result.errors
    assert result.data == expected


def test_fetch_some_id_query():
    query = '''
        query FetchSomeIDQuery($someId: String!) {
          human(id: $someId) {
            name
          }
        }
    '''
    params = {
        'someId': '1000',
    }
    expected = {
        'human': {
            'name': 'Luke Skywalker',
        }
    }
    result = Schema.execute(query, None, params)
    assert not result.errors
    assert result.data == expected


def test_fetch_some_id_query2():
    query = '''
        query FetchSomeIDQuery($someId: String!) {
          human(id: $someId) {
            name
          }
        }
    '''
    params = {
        'someId': '1002',
    }
    expected = {
        'human': {
            'name': 'Han Solo',
        }
    }
    result = Schema.execute(query, None, params)
    assert not result.errors
    assert result.data == expected


def test_invalid_id_query():
    query = '''
        query humanQuery($id: String!) {
          human(id: $id) {
            name
          }
        }
    '''
    params = {
        'id': 'not a valid id',
    }
    expected = {
        'human': None
    }
    result = Schema.execute(query, None, params)
    assert not result.errors
    assert result.data == expected


def test_fetch_luke_aliased():
    query = '''
        query FetchLukeAliased {
          luke: human(id: "1000") {
            name
          }
        }
    '''
    expected = {
        'luke': {
            'name': 'Luke Skywalker',
        }
    }
    result = Schema.execute(query)
    assert not result.errors
    assert result.data == expected


def test_fetch_luke_and_leia_aliased():
    query = '''
        query FetchLukeAndLeiaAliased {
          luke: human(id: "1000") {
            name
          }
          leia: human(id: "1003") {
            name
          }
        }
    '''
    expected = {
        'luke': {
            'name': 'Luke Skywalker',
        },
        'leia': {
            'name': 'Leia Organa',
        }
    }
    result = Schema.execute(query)
    assert not result.errors
    assert result.data == expected


def test_duplicate_fields():
    query = '''
        query DuplicateFields {
          luke: human(id: "1000") {
            name
            homePlanet
          }
          leia: human(id: "1003") {
            name
            homePlanet
          }
        }
    '''
    expected = {
        'luke': {
            'name': 'Luke Skywalker',
            'homePlanet': 'Tatooine',
        },
        'leia': {
            'name': 'Leia Organa',
            'homePlanet': 'Alderaan',
        }
    }
    result = Schema.execute(query)
    assert not result.errors
    assert result.data == expected


def test_use_fragment():
    query = '''
        query UseFragment {
          luke: human(id: "1000") {
            ...HumanFragment
          }
          leia: human(id: "1003") {
            ...HumanFragment
          }
        }
        fragment HumanFragment on Human {
          name
          homePlanet
        }
    '''
    expected = {
        'luke': {
            'name': 'Luke Skywalker',
            'homePlanet': 'Tatooine',
        },
        'leia': {
            'name': 'Leia Organa',
            'homePlanet': 'Alderaan',
        }
    }
    result = Schema.execute(query)
    assert not result.errors
    assert result.data == expected


def test_check_type_of_r2():
    query = '''
        query CheckTypeOfR2 {
          hero {
            __typename
            name
          }
        }
    '''
    expected = {
        'hero': {
            '__typename': 'Droid',
            'name': 'R2-D2',
        }
    }
    result = Schema.execute(query)
    assert not result.errors
    assert result.data == expected


def test_check_type_of_luke():
    query = '''
        query CheckTypeOfLuke {
          hero(episode: EMPIRE) {
            __typename
            name
          }
        }
    '''
    expected = {
        'hero': {
            '__typename': 'Human',
            'name': 'Luke Skywalker',
        }
    }
    result = Schema.execute(query)
    assert not result.errors
    assert result.data == expected
