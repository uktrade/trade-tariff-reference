from unittest import mock

import pytest

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
