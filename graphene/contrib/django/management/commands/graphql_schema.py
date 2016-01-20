import importlib
import json
from distutils.version import StrictVersion
from optparse import make_option

from django import get_version as get_django_version
from django.core.management.base import BaseCommand, CommandError

LT_DJANGO_1_8 = StrictVersion(get_django_version()) < StrictVersion('1.8')

if LT_DJANGO_1_8:
    class CommandArguments(BaseCommand):
        option_list = BaseCommand.option_list + (
            make_option(
                '--schema',
                type=str,
                dest='schema',
                default='',
                help='Django app containing schema to dump, e.g. myproject.core.schema',
            ),
            make_option(
                '--out',
                type=str,
                dest='out',
                default='',
                help='Output file (default: schema.json)'
            ),
        )
else:
    class CommandArguments(BaseCommand):

        def add_arguments(self, parser):
            from django.conf import settings
            parser.add_argument(
                '--schema',
                type=str,
                dest='schema',
                default=getattr(settings, 'GRAPHENE_SCHEMA', ''),
                help='Django app containing schema to dump, e.g. myproject.core.schema')

            parser.add_argument(
                '--out',
                type=str,
                dest='out',
                default=getattr(settings, 'GRAPHENE_SCHEMA_OUTPUT', 'schema.json'),
                help='Output file (default: schema.json)')


class Command(CommandArguments):
    help = 'Dump Graphene schema JSON to file'
    can_import_settings = True

    def save_file(self, out, schema_dict):
        with open(out, 'w') as outfile:
            json.dump(schema_dict, outfile)

    def handle(self, *args, **options):
        from django.conf import settings
        schema = options.get('schema') or getattr(settings, 'GRAPHENE_SCHEMA', '')
        out = options.get('out') or getattr(settings, 'GRAPHENE_SCHEMA_OUTPUT', 'schema.json')

        if schema == '':
            raise CommandError('Specify schema on GRAPHENE_SCHEMA setting or by using --schema')
        i = importlib.import_module(schema)

        schema_dict = {'data': i.schema.introspect()}
        self.save_file(out, schema_dict)

        style = getattr(self, 'style', None)
        SUCCESS = getattr(style, 'SUCCESS', lambda x: x)

        self.stdout.write(SUCCESS('Successfully dumped GraphQL schema to %s' % out))
