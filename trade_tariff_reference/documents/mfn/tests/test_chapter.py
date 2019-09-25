import zipfile
from unittest import mock

from override_storage import override_storage

import pytest

from trade_tariff_reference.documents.mfn.application import Application
from trade_tariff_reference.documents.mfn.chapter import ClassificationChapter, ScheduleChapter, process_chapter
from trade_tariff_reference.documents.mfn.constants import CLASSIFICATION, SCHEDULE
from trade_tariff_reference.schedule.tests.factories import ChapterFactory


pytestmark = pytest.mark.django_db


class TestScheduleChapter:

    def test_initialise(self):
        application = mock.MagicMock(document_type=SCHEDULE, OUTPUT_DIR='/tmp')
        db_chapter = ChapterFactory(id=1, description='Test')
        chapter = ScheduleChapter(application, db_chapter)
        assert chapter.footnote_list == []
        assert chapter.duty_list == []
        assert chapter.supplementary_unit_list == []
        assert chapter.seasonal_records == 0
        assert chapter.contains_authorised_use is False
        assert chapter.document_title == 'UK Goods Schedule'

    @pytest.mark.parametrize(
        'chapter_id,should_chapter_be_processed',
        (
            (1, True),
            (77, False),
            (98, False),
            (99, False),
        ),
    )
    @mock.patch('trade_tariff_reference.documents.mfn.chapter.ScheduleChapter.format_chapter')
    @mock.patch('trade_tariff_reference.documents.mfn.chapter.ScheduleChapter.__init__')
    def test_process_schedule_chapter(self, mock_init, mock_format_chapter, chapter_id, should_chapter_be_processed):
        mock_format_chapter.return_value = None
        mock_init.return_value = None
        application = mock.MagicMock(document_type=SCHEDULE, OUTPUT_DIR='/tmp')
        db_chapter = ChapterFactory(id=chapter_id, description='Test')
        process_chapter(application, db_chapter.id)
        assert mock_init.called is should_chapter_be_processed
        assert mock_format_chapter.called is should_chapter_be_processed

    @override_storage()
    def test_write(self):
        file_contents = 'XML'
        real_application = Application(SCHEDULE)
        application = mock.MagicMock(
            document_type=SCHEDULE,
            OUTPUT_DIR='/tmp',
            MODEL_DIR=real_application.MODEL_DIR
        )
        db_chapter = ChapterFactory(id=1, description='Test')

        chapter = ScheduleChapter(application, db_chapter)
        actual_remote_file_name = chapter.write(file_contents)
        db_chapter.refresh_from_db()

        assert db_chapter.schedule_document.name == actual_remote_file_name
        with zipfile.ZipFile(db_chapter.schedule_document) as fh:
            actual_files = [f.filename for f in fh.filelist]
            assert set(actual_files) == {
                'word/fontTable.xml',
                'word/numbering.xml',
                'word/header1.xml',
                'docProps/core.xml',
                'word/_rels/document.xml.rels',
                'customXml/_rels/item1.xml.rels',
                'customXml/itemProps1.xml',
                'word/theme/theme1.xml',
                'word/header2.xml',
                'customXml/item1.xml',
                'docProps/app.xml',
                'word/endnotes.xml',
                'word/footer1.xml',
                'word/webSettings.xml',
                'word/styles.xml',
                '_rels/.rels',
                'word/settings.xml',
                'word/footnotes.xml',
                'word/document.xml',
                '[Content_Types].xml'
            }
            actual_document_xml = fh.read('word/document.xml')
            assert actual_document_xml == bytes(file_contents, 'utf-8')


class TestClassificationChapter:

    def test_initialise(self):
        application = mock.MagicMock(document_type=CLASSIFICATION, OUTPUT_DIR='/tmp')
        db_chapter = ChapterFactory(id=1, description='Test')
        chapter = ClassificationChapter(application, db_chapter)
        assert chapter.footnote_list == []
        assert chapter.duty_list == []
        assert chapter.supplementary_unit_list == []
        assert chapter.seasonal_records == 0
        assert chapter.contains_authorised_use is False
        assert chapter.document_title == 'UK Goods Classification'

    @mock.patch('trade_tariff_reference.documents.mfn.chapter.ClassificationChapter.format_chapter')
    @mock.patch('trade_tariff_reference.documents.mfn.chapter.ClassificationChapter.__init__')
    def test_process_schedule_chapter(self, mock_init, mock_format_chapter):
        mock_format_chapter.return_value = None
        mock_init.return_value = None
        application = mock.MagicMock(document_type=CLASSIFICATION, OUTPUT_DIR='/tmp')
        db_chapter = ChapterFactory(id=1, description='Test')
        process_chapter(application, db_chapter.id)
        assert mock_init.called
        assert mock_format_chapter.called

    @override_storage()
    @mock.patch('trade_tariff_reference.documents.mfn.chapter.ClassificationChapter.prepend_introduction')
    @mock.patch('trade_tariff_reference.documents.mfn.chapter.ClassificationChapter.get_section_details')
    @mock.patch('trade_tariff_reference.documents.mfn.chapter.ClassificationChapter.get_duties')
    def test_write(self, mock_get_duties, mock_get_section_details, mock_prepend_introduction):
        mock_get_duties.return_value = None
        mock_get_section_details.return_value = None
        mock_prepend_introduction.return_value = None

        file_contents = 'XML'
        application = Application(CLASSIFICATION)
        db_chapter = ChapterFactory(id=1, description='Test')
        chapter = ClassificationChapter(application, db_chapter)
        actual_remote_file_name = chapter.write(file_contents)
        assert mock_prepend_introduction.called is True
        db_chapter.refresh_from_db()

        assert db_chapter.classification_document.name == actual_remote_file_name
        with zipfile.ZipFile(db_chapter.classification_document) as fh:
            actual_files = [f.filename for f in fh.filelist]
            assert set(actual_files) == {
                'word/fontTable.xml',
                'word/numbering.xml',
                'word/header1.xml',
                'docProps/core.xml',
                'word/_rels/document.xml.rels',
                'customXml/_rels/item1.xml.rels',
                'customXml/itemProps1.xml',
                'word/theme/theme1.xml',
                'word/header2.xml',
                'customXml/item1.xml',
                'docProps/app.xml',
                'word/endnotes.xml',
                'word/footer1.xml',
                'word/webSettings.xml',
                'word/styles.xml',
                '_rels/.rels',
                'word/settings.xml',
                'word/footnotes.xml',
                'word/document.xml',
                '[Content_Types].xml'
            }
            actual_document_xml = fh.read('word/document.xml')
            assert actual_document_xml == bytes(file_contents, 'utf-8')
