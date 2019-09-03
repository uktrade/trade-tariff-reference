import tempfile
from unittest import mock

from django.utils import timezone

from freezegun import freeze_time

from override_storage import override_storage

import pytest

from trade_tariff_reference.documents.history import MFNDocumentHistoryLog
from trade_tariff_reference.documents.mfn.constants import CLASSIFICATION, SCHEDULE
from trade_tariff_reference.documents.mfn_master.application import Application
from trade_tariff_reference.documents.utils import get_document_check_sum
from trade_tariff_reference.schedule.models import (
    DocumentStatus,
    MFNDocument,
    MFNDocumentHistory,
)
from trade_tariff_reference.schedule.tests.factories import (
    ChapterFactory,
    ChapterWithDocumentFactory,
    MFNDocumentFactory,
)

pytestmark = pytest.mark.django_db

schedule_checksum = get_document_check_sum('hello'.encode('utf-8'))
classification_checksum = get_document_check_sum('goodbye'.encode('utf-8'))


class FakeComposer:
    documents = []
    remote_file_name = None

    def __init__(self, initial_document):
        self.initial_document = initial_document

    @classmethod
    def save(cls, remote_file_name):
        cls.remote_file_name = remote_file_name

    @classmethod
    def append(cls, value):
        cls.documents.append(value)


def test_initialise_without_force():
    app = Application(SCHEDULE)
    assert app.force is False
    assert app.document_type == SCHEDULE


def test_initialise_with_force():
    app = Application(CLASSIFICATION, force=True)
    assert app.force is True
    assert app.document_type == CLASSIFICATION


@mock.patch('trade_tariff_reference.documents.mfn_master.application.update_document_status')
@mock.patch('trade_tariff_reference.documents.mfn_master.application.Application.create_document')
def test_main_updates_document_status(mock_create_document, mock_update_status):
    mfn_document = MFNDocumentFactory(document_type=SCHEDULE)
    mock_create_document.return_value = None
    app = Application(SCHEDULE)
    app.main()
    assert mock_create_document.call_count == 1
    assert mock_update_status.call_count == 2
    assert mock_update_status.call_args_list[0] == mock.call(mfn_document, DocumentStatus.GENERATING)
    assert mock_update_status.call_args_list[1] == mock.call(mfn_document, DocumentStatus.AVAILABLE)


@mock.patch('trade_tariff_reference.documents.mfn_master.application.update_document_status')
@mock.patch('trade_tariff_reference.documents.mfn_master.application.Application.create_document')
def test_main_updates_document_status_when_mfn_document_does_not_exist(mock_create_document, mock_update_status):
    mock_create_document.return_value = None
    app = Application(SCHEDULE)
    app.main()
    assert mock_create_document.call_count == 1
    assert mock_update_status.call_count == 1
    assert mock_update_status.call_args_list[0] == mock.call(None, DocumentStatus.AVAILABLE)


@pytest.mark.parametrize(
    'document_type,expected_checksum',
    (
        (SCHEDULE, schedule_checksum),
        (CLASSIFICATION, classification_checksum),
    )
)
def test_get_change_dict(document_type, expected_checksum):
    chapter = ChapterFactory()
    chapter_with_checksum = ChapterFactory(
        id=2,
        schedule_document_check_sum=schedule_checksum,
        classification_document_check_sum=classification_checksum,
    )
    app = Application(document_type)
    actual_change_dict = app.get_change_dict()
    assert actual_change_dict == {
        chapter.get_document_name(document_type): None,
        chapter_with_checksum.get_document_name(document_type): expected_checksum,
    }


@mock.patch('trade_tariff_reference.documents.mfn_master.application.Document')
@mock.patch('trade_tariff_reference.documents.mfn_master.application.Composer')
def test_merge_documents(mock_composer, mock_document):
    fake_composer = FakeComposer
    mock_document.return_value = None
    mock_document.side_effect = ['1', '2']
    mock_composer.return_value = fake_composer
    ChapterWithDocumentFactory(id=1)
    ChapterWithDocumentFactory(id=2)
    app = Application(SCHEDULE)
    app.merge_documents('schedule_document', '1.txt')
    mock_composer.assert_called_once_with('1')
    assert fake_composer.documents == ['2']
    assert fake_composer.remote_file_name == '1.txt'


@override_storage()
@freeze_time('2011-02-16 10:00:00')
def test_upload_document_when_mfn_document_does_not_exist():
    app = Application(SCHEDULE)
    fake_file_content = b'information'
    with tempfile.NamedTemporaryFile() as f:
        f.write(fake_file_content)
        f.seek(0)
        app.upload_document(None, f.name, '1.docx')

    mfn_document = MFNDocument.objects.get(document_type=SCHEDULE)
    assert mfn_document.document.read() == fake_file_content
    assert mfn_document.document_check_sum == 'bb3ccd5881d651448ded1dac904054ac'
    assert mfn_document.document_created_at == timezone.now()
    assert mfn_document.document_status == DocumentStatus.UNAVAILABLE


@override_storage()
@freeze_time('2011-02-16 10:00:00')
def test_upload_document_when_mfn_document_exists():
    mfn_document = MFNDocumentFactory(
        document_check_sum='hello',
        document_type=SCHEDULE,
        document_status=DocumentStatus.AVAILABLE,
    )
    app = Application(SCHEDULE)
    fake_file_content = b'information'
    with tempfile.NamedTemporaryFile() as f:
        f.write(fake_file_content)
        f.seek(0)
        app.upload_document(mfn_document, f.name, '1.docx')

    mfn_document.refresh_from_db()
    assert mfn_document.document.read() == fake_file_content
    assert mfn_document.document_check_sum == 'bb3ccd5881d651448ded1dac904054ac'
    assert mfn_document.document_created_at == timezone.now()
    assert mfn_document.document_status == DocumentStatus.AVAILABLE


@pytest.mark.parametrize(
    'force,add_chapters,expected_result',
    (
        (False, False, False),
        (True, False, True),
        (False, True, True),
        (True, True, True),

    ),
)
@mock.patch('trade_tariff_reference.documents.mfn_master.application.Application.write_document')
def test_create_document(
    mock_create_document,
    force,
    add_chapters,
    expected_result
):
    mock_create_document.return_value = None
    if add_chapters:
        ChapterFactory()
    mfn_document = MFNDocumentFactory(document_type=SCHEDULE)
    app = Application(SCHEDULE, force=force)
    app.create_document(mfn_document)
    assert mock_create_document.called is expected_result


@mock.patch('trade_tariff_reference.documents.mfn_master.application.Application.merge_documents')
@mock.patch('trade_tariff_reference.documents.mfn_master.application.Application.upload_document')
def test_write_document(mock_upload_document, mock_merge_documents):
    mock_merge_documents.return_value = None
    mock_upload_document.return_value = None
    forced = False
    app = Application(SCHEDULE)
    mfn_document = MFNDocumentFactory(document_type=SCHEDULE)
    mfn_history_log = MFNDocumentHistoryLog(
        mfn_document,
        {},
        forced,
        SCHEDULE,
    )
    app.write_document(mfn_document, mfn_history_log)
    assert mock_upload_document.called is True
    assert mock_merge_documents.called is True
    actual_history = MFNDocumentHistory.objects.get(
        mfn_document=mfn_document,
    )
    assert actual_history.change == {}
    assert actual_history.remote_file_name == 'schedule.docx'
    assert actual_history.forced == forced
    assert actual_history.document_type == SCHEDULE
