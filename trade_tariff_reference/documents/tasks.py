from celery import shared_task

from trade_tariff_reference.documents.fta.application import Application
from trade_tariff_reference.schedule.models import Agreement


@shared_task
def generate_document(country_profile, force=False):
    app = Application(country_profile=country_profile, force_document_generation=force)
    app.create_document()
    app.shutDown()


@shared_task
def generate_all_documents(force, background):
    agreements = Agreement.objects.all().order_by('slug')
    for agreement in agreements:
        if background:
            generate_document.delay(agreement.country_profile, force=force)
        else:
            generate_document(agreement.country_profile, force=force)
