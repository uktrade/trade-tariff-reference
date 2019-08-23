import tempfile

from django.utils import timezone

from freezegun import freeze_time

from override_storage import override_storage

import pytest

from trade_tariff_reference.documents.utils import (
    update_agreement_document_status,
    upload_document_to_s3,
    upload_generic_document_to_s3
)

from trade_tariff_reference.schedule.models import Agreement, DocumentStatus
from trade_tariff_reference.schedule.tests.factories import AgreementFactory, ChapterFactory


pytestmark = pytest.mark.django_db


@override_storage()
@freeze_time('2011-02-16 10:00:00')
def test_upload_document_to_s3():
    agreement = AgreementFactory()
    fake_file_content = b'information'
    with tempfile.NamedTemporaryFile() as f:
        f.write(fake_file_content)
        f.seek(0)
        actual_remote_file_name = upload_document_to_s3(agreement, f.name)
        agreement.refresh_from_db()
        assert agreement.document.read() == fake_file_content
        assert actual_remote_file_name.endswith('docx')
        assert agreement.document_created_at == timezone.now()


@override_storage()
@freeze_time('2011-02-16 10:00:00')
def test_upload_generic_document_to_s3():
    chapter = ChapterFactory()
    fake_file_content = b'information'
    with tempfile.NamedTemporaryFile() as f:
        f.write(fake_file_content)
        f.seek(0)
        actual_remote_file_name = upload_generic_document_to_s3(chapter, 'schedule_document', f.name, '1.docx')
        chapter.refresh_from_db()
        assert chapter.schedule_document.read() == fake_file_content
        assert actual_remote_file_name.endswith('docx')
        assert chapter.schedule_document_created_at == timezone.now()


def test_update_agreement_document_status():
    agreement = AgreementFactory()
    update_agreement_document_status(agreement, DocumentStatus.UNAVAILABLE)
    agreement.refresh_from_db()
    assert agreement.document_status == DocumentStatus.UNAVAILABLE
