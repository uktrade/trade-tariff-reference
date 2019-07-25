from django.core.management.base import BaseCommand

from trade_tariff_reference.documents.tasks import generate_all_documents


class Command(BaseCommand):

    help = ''

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force all documents to be generated even if no changes are found',
            default=False,
        )
        parser.add_argument(
            '--background',
            action='store_true',
            help='Create the documents in a background process',
            default=False,
        )

    def handle(self, *args, **options):
        generate_all_documents(options['force'], options['background'])
