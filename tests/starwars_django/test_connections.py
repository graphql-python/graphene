# import pytest
# from graphql.core import graphql

# from .models import *
# from .schema import schema
# from .data import initialize, getFaction

# pytestmark = pytest.mark.django_db

# def test_correct_fetch_first_ship_rebels():
#     initialize()
#     print schema.Faction._meta.fields_map
#     query = '''
#     query RebelsShipsQuery {
#       rebels {
#         name,
#         ships(first: 1) {
#           edges {
#             node {
#               name
#             }
#           }
#         }
#       }
#     }
#     '''
#     expected = {
#       'rebels': {
#         'name': 'Alliance to Restore the Republic',
#         'ships': {
#           'edges': [
#             {
#               'node': {
#                 'name': 'X-Wing'
#               }
#             }
#           ]
#         }
#       }
#     }
#     result = schema.execute(query)
#     assert not result.errors
#     assert result.data == expected
