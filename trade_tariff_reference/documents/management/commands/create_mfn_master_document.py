from django.core.management.base import BaseCommand

from trade_tariff_reference.documents.mfn.constants import CLASSIFICATION, SCHEDULE
from trade_tariff_reference.documents.tasks import generate_mfn_master_document


class Command(BaseCommand):

    help = 'Command to combine all schedule/classification chapters in to one document'

    def add_arguments(self, parser):
        parser.add_argument('document_type', type=str, choices=[SCHEDULE, CLASSIFICATION])
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force document to be generated even if no changes are found',
            default=False,
        )
        parser.add_argument(
            '--background',
            action='store_true',
            help='Create the document in a background process',
            default=False,
        )

    def handle(self, *args, **options):
        document_type = options['document_type']
        force = options['force']
        if options['background']:
            generate_mfn_master_document.delay(document_type, force)
        else:
            generate_mfn_master_document(document_type, force)
