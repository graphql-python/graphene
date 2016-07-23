from graphene import ObjectType, Schema, String

from ..utils import get_session


def test_get_session():
    session = 'My SQLAlchemy session'

    class Query(ObjectType):
        x = String()

        def resolve_x(self, args, context, info):
            return get_session(context)

    query = '''
        query ReporterQuery {
            x
        }
    '''

    schema = Schema(query=Query)
    result = schema.execute(query, context_value={'session': session})
    assert not result.errors
    assert result.data['x'] == session
