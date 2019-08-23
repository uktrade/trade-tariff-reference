from celery import shared_task

from trade_tariff_reference.documents.fta.application import Application as FTAApplication
from trade_tariff_reference.documents.mfn.application import Application as MFNApplication
from trade_tariff_reference.documents.utils import update_agreement_document_status
from trade_tariff_reference.schedule.models import Agreement, DocumentStatus


def handle_document_generation_fail(self, exc, task_id, args, kwargs, einfo):
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
        update_agreement_document_status(agreement, DocumentStatus.UNAVAILABLE)


@shared_task(
    autoretry_for=(Exception,),
    max_retries=3,
    retry_backoff=30,
    on_failure=handle_document_generation_fail,
)
def generate_fta_document(country_profile, force=False):
    app = FTAApplication(
        country_profile=country_profile,
        force_document_generation=force,
    )
    app.main()


@shared_task
def generate_all_fta_documents(force, background):
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
    on_failure=handle_document_generation_fail,
)
def generate_mfn_document(document_type, first_chapter, last_chapter, force=False):
    app = MFNApplication(document_type, first_chapter=first_chapter, last_chapter=last_chapter)
    app.main()
