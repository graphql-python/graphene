from pytest import raises
from graphql.core import graphql

from .schema import Schema

def test_correct_fetch_first_ship_rebels():
    query = '''
    query RebelsShipsQuery {
      rebels {
        name,
        ships(first: 1) {
          edges {
            node {
              name
            }
          }
        }
      }
    }
    '''
    expected = {
      'rebels': {
        'name': 'Alliance to Restore the Republic',
        'ships': {
          'edges': [
            {
              'node': {
                'name': 'X-Wing'
              }
            }
          ]
        }
      }
    }
    result = Schema.execute(query)
    assert result.errors == None
    assert result.data == expected
