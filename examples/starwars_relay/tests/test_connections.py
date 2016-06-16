from ..data import setup
from ..schema import schema

setup()


def test_correct_fetch_first_ship_rebels():
    query = '''
    query RebelsShipsQuery {
      rebels {
        name,
        ships(first: 1) {
          pageInfo {
            startCursor
            endCursor
            hasNextPage
            hasPreviousPage
          }
          edges {
            cursor
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
                'pageInfo': {
                    'startCursor': 'YXJyYXljb25uZWN0aW9uOjA=',
                    'endCursor': 'YXJyYXljb25uZWN0aW9uOjA=',
                    'hasNextPage': True,
                    'hasPreviousPage': False
                },
                'edges': [
                    {
                        'cursor': 'YXJyYXljb25uZWN0aW9uOjA=',
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
