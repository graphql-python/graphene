from graphene import ObjectType, Schema, String

from ..utils import get_session


def test_get_session():
    session = 'My SQLAlchemy session'
    schema = Schema(session=session)

    class Query(ObjectType):
        x = String()

        def resolve_x(self, args, info):
            return get_session(info)

    query = '''
        query ReporterQuery {
            x
        }
    '''

    schema = Schema(query=Query, session=session)
    result = schema.execute(query)
    assert not result.errors
    assert result.data['x'] == session
