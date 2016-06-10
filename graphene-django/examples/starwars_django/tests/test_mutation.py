import pytest

from ..data import initialize
from ..schema import schema

pytestmark = pytest.mark.django_db


def test_mutations():
    initialize()

    query = '''
    mutation MyMutation {
      introduceShip(input:{clientMutationId:"abc", shipName: "Peter", factionId: "1"}) {
        ship {
          id
          name
        }
        faction {
          name
          ships {
            edges {
              node {
                id
                name
              }
            }
          }
        }
      }
    }
    '''
    expected = {
        'introduceShip': {
            'ship': {
                'id': 'U2hpcDo5',
                'name': 'Peter'
            },
            'faction': {
                'name': 'Alliance to Restore the Republic',
                'ships': {
                    'edges': [{
                        'node': {
                            'id': 'U2hpcDox',
                            'name': 'X-Wing'
                        }
                    }, {
                        'node': {
                            'id': 'U2hpcDoy',
                            'name': 'Y-Wing'
                        }
                    }, {
                        'node': {
                            'id': 'U2hpcDoz',
                            'name': 'A-Wing'
                        }
                    }, {
                        'node': {
                            'id': 'U2hpcDo0',
                            'name': 'Millenium Falcon'
                        }
                    }, {
                        'node': {
                            'id': 'U2hpcDo1',
                            'name': 'Home One'
                        }
                    }, {
                        'node': {
                            'id': 'U2hpcDo5',
                            'name': 'Peter'
                        }
                    }]
                },
            }
        }
    }
    result = schema.execute(query)
    assert not result.errors
    assert result.data == expected
