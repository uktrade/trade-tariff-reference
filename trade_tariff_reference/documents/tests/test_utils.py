import tempfile

from django.utils import timezone

from freezegun import freeze_time

from override_storage import override_storage

import pytest

from trade_tariff_reference.documents.utils import upload_document_to_s3
from trade_tariff_reference.schedule.tests.factories import AgreementFactory


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
