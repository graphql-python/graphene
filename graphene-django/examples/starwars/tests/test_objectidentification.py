import pytest

from ..data import initialize
from ..schema import schema

pytestmark = pytest.mark.django_db


def test_correctly_fetches_id_name_rebels():
    initialize()
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
    initialize()
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
    initialize()
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
    initialize()
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
    initialize()
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
