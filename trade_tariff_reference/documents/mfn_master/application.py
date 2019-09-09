import logging
import tempfile

from django.db import transaction

from docx import Document

from docxcompose.composer import Composer

from trade_tariff_reference.documents.history import MFNDocumentHistoryLog
from trade_tariff_reference.documents.utils import (
    update_document_status,
    update_last_checked,
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

    def get_object(self):
        try:
            return MFNDocument.objects.get(document_type=self.document_type)
        except MFNDocument.DoesNotExist:
            pass

    def main(self):
        mfn_document = self.get_object()
        if mfn_document:
            update_document_status(mfn_document, DocumentStatus.GENERATING)
        self.create_document(mfn_document)
        mfn_document = self.get_object()
        update_document_status(mfn_document, DocumentStatus.AVAILABLE)
        update_last_checked(mfn_document)

    def write_document(self, mfn_document, mfn_document_log):
        document_field = f"{self.document_type}_document"
        file_name = f'{self.document_type}.docx'

        with tempfile.TemporaryDirectory(prefix='mfn_complete') as tmp_dir:
            full_file_name = f'{tmp_dir}/{file_name}'
            self.merge_documents(document_field, full_file_name)
            self.upload_document(mfn_document, full_file_name, file_name)
        mfn_document_log.log_document_history(file_name)
        logger.info(f"PROCESS COMPLETE - Master MFN {file_name} created")

    @transaction.atomic
    def create_document(self, mfn_document):
        mfn_document_log = MFNDocumentHistoryLog(
            mfn_document,
            self.get_change_dict(),
            False,
            self.document_type
        )
        if mfn_document_log.change or self.force:
            self.write_document(mfn_document, mfn_document_log)
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
        chapters = Chapter.objects.all()
        first_chapter = chapters.first()
        master_document = self.get_docx(first_chapter, document_field)
        complete_document = Composer(master_document)
        logger.info(f'Processing {self.document_type} {first_chapter.chapter_string}')
        for chapter in chapters.exclude(id=first_chapter.id):
            logger.info(f'Processing {self.document_type} {chapter.chapter_string}')
            docx = self.get_docx(chapter, document_field)
            complete_document.append(docx)
        complete_document.save(full_file_name)

    def get_docx(self, chapter, document_field):
        document = getattr(chapter, document_field)
        return Document(document)
