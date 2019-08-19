from trade_tariff_reference.documents.tasks import generate_fta_document
from trade_tariff_reference.documents.utils import update_agreement_document_status


def generate_document(agreement):
    update_agreement_document_status(agreement, agreement.GENERATING)
    generate_fta_document.delay(agreement.slug)
