from celery import shared_task

from trade_tariff_reference.documents.fta.application import Application as FTAApplication
from trade_tariff_reference.documents.mfn.chapter import Chapter
from trade_tariff_reference.documents.mfn.application import Application as MFNApplication

from trade_tariff_reference.documents.utils import update_agreement_document_status
from trade_tariff_reference.schedule.models import Agreement


def handle_document_generation_fail(self, exc, task_id, args, kwargs, einfo):
    if not args:
        return
    slug = args[0]
    try:
        agreement = Agreement.objects.get(
            slug=slug,
            document_status=Agreement.GENERATING
        )
    except Agreement.DoesNotExist:
        pass
    else:
        update_agreement_document_status(agreement, Agreement.UNAVAILABLE)


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
    app.create_document()
    app.shutDown()


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
def generate_mfn_document(force=False):
    app = MFNApplication()
    app.get_sections_chapters()
    app.read_templates()
    if app.document_type == "schedule":
        app.get_authorised_use_commodities()
        app.get_seasonal()
        app.get_special_notes()
    for i in range(app.first_chapter, app.last_chapter + 1):
        oChapter = Chapter(app, i)
        # Need to fix and reinstate
        # oChapter.format_chapter()
    app.shutDown()
