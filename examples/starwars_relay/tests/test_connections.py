from graphene.test import Client

from ..data import setup
from ..schema import schema

setup()

client = Client(schema)


def test_correct_fetch_first_ship_rebels():
    result = client.execute("""
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
    """)
    assert result == {
        "data": {
            "rebels": {
                "name": "Alliance to Restore the Republic",
                "ships": {
                    "pageInfo": {
                        "startCursor": "YXJyYXljb25uZWN0aW9uOjA=",
                        "endCursor": "YXJyYXljb25uZWN0aW9uOjA=",
                        "hasNextPage": True,
                        "hasPreviousPage": False,
                    },
                    "edges": [
                        {
                            "cursor": "YXJyYXljb25uZWN0aW9uOjA=",
                            "node": {"name": "X-Wing"},
                        }
                    ],
                },
            }
        }
    }
