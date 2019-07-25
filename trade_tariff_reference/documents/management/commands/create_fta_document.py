from django.core.management.base import BaseCommand

from trade_tariff_reference.documents.tasks import generate_document


class Command(BaseCommand):

    help = ''

    def add_arguments(self, parser):
        parser.add_argument('country_profile', type=str)
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force the document to be generated even if no changes are found',
            default=False,
        )
        parser.add_argument(
            '--background',
            action='store_true',
            help='Create  document in a background process',
            default=False,
        )

    def handle(self, *args, **options):
        if options['background']:
            generate_document.delay(options['country_profile'], options['force'])
        else:
            generate_document(options['country_profile'], options['force'])
