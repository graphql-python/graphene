import importlib
import json

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Dump Graphene schema JSON to file'
    can_import_settings = True

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

    def handle(self, *args, **options):
        schema_module = options['schema']
        if schema_module == '':
            raise CommandError('Specify schema on GRAPHENE_SCHEMA setting or by using --schema')
        i = importlib.import_module(schema_module)

        schema_dict = {'data': i.schema.introspect()}

        with open(options['out'], 'w') as outfile:
            json.dump(schema_dict, outfile)

        self.stdout.write(self.style.SUCCESS('Successfully dumped GraphQL schema to %s' % options['out']))
