from django.core.management.base import BaseCommand

from documents.fta.application import Application


class Appy:
    app = Application()

class Command(BaseCommand):

    help = ''



    def handle(self, *args, **options):
        global g
        g = Appy()

        g.app.get_sections_chapters()
        g.app.create_document()
        g.app.shutDown()
