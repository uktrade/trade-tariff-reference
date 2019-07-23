from celery import shared_task
from trade_tariff_reference.documents.fta.application import Application


@shared_task
def generate_document(country_profile):
    app = Application(country_profile=country_profile)
    app.create_document()
    app.shutDown()
