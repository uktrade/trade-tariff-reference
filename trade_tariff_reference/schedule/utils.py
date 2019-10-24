from trade_tariff_reference.documents.tasks import generate_fta_document
from trade_tariff_reference.documents.utils import update_document_status
from trade_tariff_reference.schedule.models import DocumentStatus


def generate_document(agreement):
    update_document_status(agreement, DocumentStatus.GENERATING)
    generate_fta_document.delay(agreement.slug)


def get_initial_quotas(agreement, lst=False):
    return {
        'origin_quotas': get_initial_origin_quotas(agreement, lst=lst),
        'licensed_quotas': get_initial_licensed_quotas(agreement, lst=lst),
        'scope_quotas': get_initial_scope_quotas(agreement, lst=lst),
        'staging_quotas': get_initial_staging_quotas(agreement, lst=lst)
    }


def get_initial_origin_quotas(agreement, lst=False):
    quotas = [quota.origin_quota_string for quota in agreement.origin_quotas]
    if lst:
        return quotas
    return '\r\n'.join(quotas)


def get_initial_licensed_quotas(agreement, lst=False):
    quotas = [quota.licensed_quota_string for quota in agreement.licensed_quotas]
    if lst:
        return quotas
    return '\r\n'.join(quotas)


def get_initial_scope_quotas(agreement, lst=False):
    quotas = [quota.scope_quota_string for quota in agreement.scope_quotas]
    if lst:
        return quotas
    return '\r\n'.join(quotas)


def get_initial_staging_quotas(agreement, lst=False):
    quotas = [quota.staging_quota_string for quota in agreement.staging_quotas]
    if lst:
        return quotas
    return '\r\n'.join(quotas)
