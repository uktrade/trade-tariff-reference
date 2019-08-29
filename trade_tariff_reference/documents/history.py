import logging

from deepdiff import DeepDiff
from deepdiff.model import PrettyOrderedSet

from trade_tariff_reference.schedule.models import AgreementDocumentHistory, ChapterDocumentHistory

logger = logging.getLogger(__name__)


def check_fta_document_for_update(agreement, context):
    history = AgreementDocumentHistory.objects.filter(
        agreement=agreement,
    ).first()
    return get_change(getattr(history, 'data', None), context)


def check_mfn_document_for_update(chapter, chapter_type, context):
    history = ChapterDocumentHistory.objects.filter(
        chapter=chapter,
        chapter_type=chapter_type,
    ).first()
    return get_change(getattr(history, 'data', None), context)


def get_change(data, context):
    change = None
    if data:
        change = DeepDiff(data, context)
    return change


def log_fta_document_history(agreement, context, change, remote_file_name, force_document_generation):
    if change:
        logger.debug(f'Changes found\n{change}')

    AgreementDocumentHistory.objects.create(
        agreement=agreement,
        data=context,
        change=prepare_change(change),
        forced=force_document_generation,
        remote_file_name=remote_file_name,
    )


def log_mfn_document_history(chapter, chapter_type, context, change, remote_file_name, force_document_generation):
    if change:
        logger.debug(f'Changes found\n{change}')

    ChapterDocumentHistory.objects.create(
        chapter=chapter,
        chapter_type=chapter_type,
        data=context,
        change=prepare_change(change),
        forced=force_document_generation,
        remote_file_name=remote_file_name,
    )


def prepare_change(change):
    if not change:
        return change
    for key in change.keys():
        if isinstance(change[key], PrettyOrderedSet):
            change[key] = list(change[key])
    return change
