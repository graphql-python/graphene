from ..data import setup
from ..schema import schema

setup()


def test_correctly_fetches_id_name_rebels():
    query = '''
      query RebelsQuery {
        rebels {
          id
          name
        }
      }
    '''
    expected = {
        'rebels': {
            'id': 'RmFjdGlvbjox',
            'name': 'Alliance to Restore the Republic'
        }
    }
    result = schema.execute(query)
    assert not result.errors
    assert result.data == expected


def test_correctly_refetches_rebels():
    query = '''
      query RebelsRefetchQuery {
        node(id: "RmFjdGlvbjox") {
          id
          ... on Faction {
            name
          }
        }
      }
    '''
    expected = {
        'node': {
            'id': 'RmFjdGlvbjox',
            'name': 'Alliance to Restore the Republic'
        }
    }
    result = schema.execute(query)
    assert not result.errors
    assert result.data == expected


def test_correctly_fetches_id_name_empire():
    query = '''
      query EmpireQuery {
        empire {
          id
          name
        }
      }
    '''
    expected = {
        'empire': {
            'id': 'RmFjdGlvbjoy',
            'name': 'Galactic Empire'
        }
    }
    result = schema.execute(query)
    assert not result.errors
    assert result.data == expected


def test_correctly_refetches_empire():
    query = '''
      query EmpireRefetchQuery {
        node(id: "RmFjdGlvbjoy") {
          id
          ... on Faction {
            name
          }
        }
      }
    '''
    expected = {
        'node': {
            'id': 'RmFjdGlvbjoy',
            'name': 'Galactic Empire'
        }
    }
    result = schema.execute(query)
    assert not result.errors
    assert result.data == expected


def test_correctly_refetches_xwing():
    query = '''
      query XWingRefetchQuery {
        node(id: "U2hpcDox") {
          id
          ... on Ship {
            name
          }
        }
      }
    '''
    expected = {
        'node': {
            'id': 'U2hpcDox',
            'name': 'X-Wing'
        }
    }
    result = schema.execute(query)
    assert not result.errors
    assert result.data == expected
