from django.core.management.base import BaseCommand

from trade_tariff_reference.documents.tasks import generate_document


class Command(BaseCommand):

    help = ''

    def add_arguments(self, parser):
        parser.add_argument('country_profile', type=str)

    def handle(self, *args, **options):
        generate_document(options['country_profile'])
