from django.core.management.base import BaseCommand

from trade_tariff_reference.documents.tasks import generate_mfn_document


class Command(BaseCommand):

    help = ''

    def add_arguments(self, parser):
        parser.add_argument('document_type', type=str, choices=['schedule', 'classification'])
        parser.add_argument('--first_chapter', type=int, default=1, choices=range(1, 100))
        parser.add_argument('--last_chapter', type=int, default=99, choices=range(1, 100))
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
            generate_mfn_document.delay(
                options['document_type'], options['first_chapter'], options['last_chapter'], options['force']
            )
        else:
            generate_mfn_document(
                options['document_type'],  options['first_chapter'], options['last_chapter'], options['force']
            )
