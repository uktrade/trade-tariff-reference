from trade_tariff_reference.documents.tasks import generate_fta_document
from trade_tariff_reference.documents.utils import update_document_status
from trade_tariff_reference.schedule.models import DocumentStatus


def generate_document(agreement):
    update_document_status(agreement, DocumentStatus.GENERATING)
    generate_fta_document.delay(agreement.slug)
