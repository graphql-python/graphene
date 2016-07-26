from ..data import setup
from ..schema import schema

setup()


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
    result = schema.execute(query)
    assert not result.errors
    assert result.data == expected
