
from ..schema import Droid


def test_query_types():
    graphql_type = Droid._meta.graphql_type
    fields = graphql_type.get_fields()
    assert fields['friends'].parent == Droid
    assert fields
