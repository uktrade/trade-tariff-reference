from celery import shared_task

from django.utils import timezone

from trade_tariff_reference.documents.fta.application import Application as FTAApplication
from trade_tariff_reference.documents.mfn.application import Application as MFNApplication
from trade_tariff_reference.documents.mfn_master.application import Application as MFNMasterApplication
from trade_tariff_reference.documents.utils import update_document_status
from trade_tariff_reference.schedule.models import (
    Agreement,
    DocumentStatus,
    MFNDocument,
)


def handle_agreement_document_generation_fail(self, exc, task_id, args, kwargs, einfo):
    if not args:
        return
    slug = args[0]
    try:
        agreement = Agreement.objects.get(
            slug=slug,
            document_status=DocumentStatus.GENERATING
        )
    except Agreement.DoesNotExist:
        pass
    else:
        update_document_status(agreement, DocumentStatus.UNAVAILABLE)


@shared_task(
    autoretry_for=(Exception,),
    max_retries=3,
    retry_backoff=30,
    on_failure=handle_agreement_document_generation_fail,
)
def generate_fta_document(country_profile, force=False):
    app = FTAApplication(
        country_profile=country_profile,
        force_document_generation=force,
    )
    app.main()


@shared_task
def generate_all_fta_documents(background=False, force=False):
    agreements = Agreement.objects.all().order_by('slug')
    for agreement in agreements:
        if background:
            generate_fta_document.delay(agreement.country_profile, force=force)
        else:
            generate_fta_document(agreement.country_profile, force=force)


@shared_task(
    autoretry_for=(Exception,),
    max_retries=3,
    retry_backoff=30,
)
def generate_mfn_document(document_type, first_chapter=1, last_chapter=99, force=False, generate_master=True):
    app = MFNApplication(document_type, first_chapter=first_chapter, last_chapter=last_chapter, force=force)
    app.main()
    if generate_master:
        generate_mfn_master_document.delay(document_type)


@shared_task(
    autoretry_for=(Exception,),
    max_retries=3,
    retry_backoff=30,
)
def generate_mfn_master_document(document_type, force=False):
    if not is_mfn_master_document_being_generated(document_type) or force:
        app = MFNMasterApplication(document_type, force=force)
        app.main()


def get_mfn_master_document(document_type):
    try:
        return MFNDocument.objects.get(document_type=document_type)
    except MFNDocument.DoesNotExist:
        return MFNDocument.objects.create(
            document_type=document_type,
            document_created_at=timezone.now(),
        )


def is_mfn_master_document_being_generated(document_type):
    mfn_master_document = get_mfn_master_document(document_type)
    return mfn_master_document.is_document_generating
