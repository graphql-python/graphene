from django.core import management
from mock import patch
from six import StringIO


@patch('graphene.contrib.django.management.commands.graphql_schema.Command.save_file')
def test_generate_file_on_call_graphql_schema(savefile_mock, settings):
    settings.GRAPHENE_SCHEMA = 'graphene.contrib.django.tests.test_urls'
    out = StringIO()
    management.call_command('graphql_schema', schema='', stdout=out)
    assert "Successfully dumped GraphQL schema to schema.json" in out.getvalue()
