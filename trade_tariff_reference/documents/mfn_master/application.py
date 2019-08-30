import logging
import tempfile

from django.db import transaction

from docx import Document

from docxcompose.composer import Composer

from trade_tariff_reference.documents.history import MFNDocumentHistoryLog
from trade_tariff_reference.documents.utils import (
    update_document_status,
    upload_generic_document_to_s3,
)
from trade_tariff_reference.schedule.models import (
    Chapter,
    DocumentStatus,
    MFNDocument,
)

logger = logging.getLogger(__name__)


class Application:

    def __init__(self, document_type, force=False):
        self.document_type = document_type
        self.force = force

    def main(self):
        mfn_document = MFNDocument.objects.filter(document_type=self.document_type).first()
        if mfn_document:
            update_document_status(mfn_document, DocumentStatus.GENERATING)
        self.create_document(mfn_document)
        update_document_status(mfn_document, DocumentStatus.AVAILABLE)

    @transaction.atomic
    def create_document(self, mfn_document):
        mfn_document_log = MFNDocumentHistoryLog(
            mfn_document,
            self.get_change_dict(),
            False,
            self.document_type
        )
        if mfn_document_log.change or self.force:
            with tempfile.TemporaryDirectory(prefix='mfn_complete') as tmp_dir:
                document_field = f"{self.document_type}_document"
                file_name = f'{self.document_type}.docx'
                full_file_name = f'{tmp_dir}/{file_name}'
                self.merge_documents(document_field, full_file_name)
                self.upload_document(mfn_document, full_file_name, file_name)
            mfn_document_log.log_document_history(file_name)
            logger.info(f"PROCESS COMPLETE - Master MFN {file_name} created")
        else:
            logger.info(
                f'PROCESS COMPLETE - Master MFN {self.document_type} document unchanged no file generated'
            )

    def get_change_dict(self):
        change_dict = {}
        for chapter in Chapter.objects.all():
            change_dict[
                chapter.get_document_name(self.document_type)
            ] = getattr(
                chapter, f'{self.document_type}_document_check_sum'
            )
        return change_dict

    def upload_document(self, document, local_file_name, remote_file_name):
        if not document:
            document = MFNDocument(document_type=self.document_type)
        upload_generic_document_to_s3(document, 'document', local_file_name, remote_file_name)

    def merge_documents(self, document_field, full_file_name):
        chapters = Chapter.objects.filter(id__in=range(80, 100))
        first_chapter = chapters.first()
        document = getattr(first_chapter, document_field)
        master_document = Document(document)
        complete_document = Composer(master_document)
        logger.info(f'Processing {self.document_type} {first_chapter.chapter_string}')
        for chapter in chapters.exclude(id=first_chapter.id):
            logger.info(f'Processing {self.document_type} {chapter.chapter_string}')
            document = getattr(chapter, document_field)
            docx = Document(document)
            complete_document.append(docx)
            complete_document.save(full_file_name)
