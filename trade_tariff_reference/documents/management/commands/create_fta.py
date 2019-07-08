from django.core.management.base import BaseCommand

from documents.fta.application import Application


class Command(BaseCommand):

    help = ''

    def add_arguments(self, parser):
        parser.add_argument('country_profile', type=str)

    def handle(self, *args, **options):
        app = Application(country_profile=options['country_profile'])
        app.create_document()
        app.shutDown()
