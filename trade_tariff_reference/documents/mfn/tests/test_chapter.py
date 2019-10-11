import zipfile
from datetime import datetime
from unittest import mock

from botocore.exceptions import EndpointConnectionError

from override_storage import override_storage

import pytest

from trade_tariff_reference.documents.mfn.application import Application
from trade_tariff_reference.documents.mfn.chapter import ClassificationChapter, ScheduleChapter, process_chapter
from trade_tariff_reference.documents.mfn.commodity import Commodity
from trade_tariff_reference.documents.mfn.constants import CLASSIFICATION, SCHEDULE
from trade_tariff_reference.documents.mfn.duty import Duty
from trade_tariff_reference.schedule.models import ChapterDocumentHistory
from trade_tariff_reference.schedule.tests.factories import (
    ChapterFactory,
    ChapterNoteWithDocumentFactory,
    SeasonalQuotaFactory
)
from trade_tariff_reference.tariff.tests.factories import (
    MeasureComponentFactory,
    SimpleCurrentMeasureFactory,
)


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
        'chapter_id,create_chapter,should_chapter_be_processed',
        (
            (1, True, True),
            (77, True, False),
            (98, True, False),
            (99, True, False),
            (1, False, False),
        ),
    )
    @mock.patch('trade_tariff_reference.documents.mfn.chapter.ScheduleChapter.format_chapter')
    @mock.patch('trade_tariff_reference.documents.mfn.chapter.ScheduleChapter.__init__')
    def test_process_schedule_chapter(
        self,
        mock_init,
        mock_format_chapter,
        chapter_id,
        create_chapter,
        should_chapter_be_processed
    ):
        mock_format_chapter.return_value = None
        mock_init.return_value = None
        application = mock.MagicMock(document_type=SCHEDULE, OUTPUT_DIR='/tmp')
        if create_chapter:
            ChapterFactory(id=chapter_id, description='Test')
        process_chapter(application, chapter_id)
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

    @pytest.mark.parametrize(
        'context,force,expected_template,expected_document_xml,expected_change,raise_write_exception',
        (
            (
                {'fake': 'context'},
                True,
                'xml/mfn/document_schedule.xml',
                'XML',
                {'dictionary_item_added': ["root['fake']"]},
                False,
            ),
            (
                {},
                False,
                'xml/mfn/document_schedule.xml',
                None,
                {},
                False,
            ),
            (
                {'fake': 'context'},
                True,
                'xml/mfn/document_schedule.xml',
                'XML',
                {},
                True,
            ),
        ),
    )
    @mock.patch('trade_tariff_reference.documents.mfn.chapter.ScheduleChapter.get_section_details')
    @mock.patch('trade_tariff_reference.documents.mfn.chapter.ScheduleChapter.get_duties')
    @mock.patch('trade_tariff_reference.documents.mfn.chapter.ScheduleChapter.write')
    @mock.patch('trade_tariff_reference.documents.mfn.chapter.render_to_string')
    def test_create_document(
        self,
        mock_render_to_string,
        mock_write,
        mock_get_duties,
        mock_get_section_details,
        context,
        force,
        expected_template,
        expected_document_xml,
        expected_change,
        raise_write_exception,
    ):
        fake_file_name = 'fake_file.txt'

        mock_get_duties.return_value = None
        mock_get_section_details.return_value = None
        mock_write.return_value = fake_file_name
        if raise_write_exception:
            mock_write.side_effect = EndpointConnectionError(endpoint_url='')

        mock_render_to_string.return_value = expected_document_xml
        application = Application(SCHEDULE, force=force)
        db_chapter = ChapterFactory(id=1, description='Test')
        chapter = ScheduleChapter(application, db_chapter)
        chapter.create_document(context)

        if expected_document_xml:
            mock_render_to_string.assert_called_with(expected_template, context)
            mock_write.asssert_called_with(expected_document_xml)
        else:
            assert mock_render_to_string.called is False
            assert mock_write.called is False

        if expected_change:
            document_history = ChapterDocumentHistory.objects.get(
                chapter=db_chapter
            )
            assert document_history.forced is force
            assert document_history.data == context
            assert document_history.change == expected_change
            assert document_history.remote_file_name == fake_file_name
        else:
            assert ChapterDocumentHistory.objects.filter(
                chapter=db_chapter
            ).exists() is False

    def test_format_schedule_chapter_with_empty_commodity_list(self):
        application = mock.MagicMock(document_type=SCHEDULE, OUTPUT_DIR='/tmp')
        db_chapter = ChapterFactory(id=1, description='Test')
        chapter = ScheduleChapter(application, db_chapter)
        result = chapter.format_schedule_chapter([])
        assert result == {'commodity_list': []}

    def test_assign_authorised_use_commodities(self):
        SeasonalQuotaFactory(quota_order_number_id='1234567891')
        SeasonalQuotaFactory(quota_order_number_id='1234567892')
        application = mock.MagicMock(
            document_type=SCHEDULE,
            OUTPUT_DIR='/tmp',
            authorised_use_list=['1234567891', '1234567892'],
        )
        commodity_1 = Commodity(
            application,
            product_line_suffix='80',
            commodity_code='1234567891'
        )
        commodity_2 = Commodity(
            application,
            product_line_suffix='82',
            commodity_code='1234567892'
        )
        commodity_3 = Commodity(
            application,
            product_line_suffix='80',
            commodity_code='1234567893'
        )
        db_chapter = ChapterFactory(id=1, description='Test')
        chapter = ScheduleChapter(application, db_chapter)
        assert chapter.contains_authorised_use is False
        assert chapter.seasonal_records == 0
        chapter.assign_authorised_use_commodities([commodity_1, commodity_2, commodity_3])
        assert chapter.contains_authorised_use is True
        assert chapter.seasonal_records == 1

    def test_assign_duties_to_commodities(self):
        application = mock.MagicMock(
            document_type=SCHEDULE,
            OUTPUT_DIR='/tmp',
        )
        commodity_1 = Commodity(
            application,
            product_line_suffix='80',
            commodity_code='1234567891'
        )
        commodity_2 = Commodity(
            application,
            product_line_suffix='82',
            commodity_code='1234567892'
        )
        Commodity(
            application,
            product_line_suffix='80',
            commodity_code='1234567893'
        )

        duty_1 = Duty(
            commodity_code=commodity_1.commodity_code
        )
        Duty(
            commodity_code=commodity_2.commodity_code
        )
        db_chapter = ChapterFactory(id=1, description='Test')
        chapter = ScheduleChapter(application, db_chapter)
        chapter.duty_list = [duty_1]
        chapter.assign_duties_to_commodities([commodity_1])
        assert commodity_1.assigned is True
        assert commodity_1.duty_list == [duty_1]
        assert commodity_1.commodity_code_formatted == '1234 56 78 91'

    @pytest.mark.parametrize(
        'combined_duty,expected_child_combined_duty',
        (
            ('commodity 1', 'commodity 1'),
            ('', ''),
        )
    )
    def test_assign_inherited_duty_to_commodity(self, combined_duty, expected_child_combined_duty):
        application = mock.MagicMock(
            document_type=SCHEDULE,
            OUTPUT_DIR='/tmp',
        )
        commodity_1 = Commodity(
            application,
            product_line_suffix='80',
            commodity_code='1200000000',
            indents=0
        )
        commodity_1.combined_duty = combined_duty
        commodity_2 = Commodity(
            application,
            product_line_suffix='82',
            commodity_code='1211000000',
            indents=3,
        )
        commodity_3 = Commodity(
            application,
            product_line_suffix='80',
            commodity_code='1211110000',
            indents=10
        )
        db_chapter = ChapterFactory(id=1, description='Test')
        chapter = ScheduleChapter(application, db_chapter)
        actual_max_indent = chapter.assign_inherited_duty_to_commodity([commodity_1, commodity_2, commodity_3])
        assert actual_max_indent == 10
        assert commodity_2.combined_duty == expected_child_combined_duty
        assert commodity_3.combined_duty == expected_child_combined_duty

    def test_suppress_none_product_line(self):
        application = mock.MagicMock(
            document_type=SCHEDULE,
            OUTPUT_DIR='/tmp',
        )
        commodity_1 = Commodity(
            application,
            product_line_suffix='80',
            commodity_code='1200000000',
            indents=0,
        )
        commodity_2 = Commodity(
            application,
            product_line_suffix='82',
            commodity_code='1211000000',
            indents=3,
        )
        commodity_3 = Commodity(
            application,
            product_line_suffix='80',
            commodity_code='1211110000',
            indents=10
        )
        commodity_3.suppress_duty = True
        db_chapter = ChapterFactory(id=1, description='Test')
        chapter = ScheduleChapter(application, db_chapter)
        chapter.suppress_none_product_line([commodity_1, commodity_2, commodity_3])
        assert commodity_1.suppress_duty is False
        assert commodity_2.suppress_duty is True
        assert commodity_3.suppress_duty is False

    def test_unsuppress_selected_commodities(self):
        application = mock.MagicMock(
            document_type=SCHEDULE,
            OUTPUT_DIR='/tmp',
        )
        commodity_1 = Commodity(
            application,
            product_line_suffix='80',
            commodity_code='1200000000',
            indents=0,
        )
        commodity_2 = Commodity(
            application,
            product_line_suffix='82',
            commodity_code='8708701080',
            indents=3,
        )
        commodity_3 = Commodity(
            application,
            product_line_suffix='80',
            commodity_code='1211110000',
            indents=10
        )
        commodity_1.suppress_duty = True
        commodity_2.suppress_duty = True
        commodity_3.suppress_duty = True

        db_chapter = ChapterFactory(id=1, description='Test')
        chapter = ScheduleChapter(application, db_chapter)
        chapter.unsuppress_selected_commodities([commodity_1, commodity_2, commodity_3])
        assert commodity_1.suppress_duty is True
        assert commodity_2.suppress_duty is False
        assert commodity_3.suppress_duty is True

    def test_suppress_row_for_commodity_when_lowest_child_is_assigned(self):
        application = mock.MagicMock(
            document_type=SCHEDULE,
            OUTPUT_DIR='/tmp',
        )
        commodity_1 = Commodity(
            application,
            product_line_suffix='80',
            commodity_code='1200000000',
            indents=0,
        )
        commodity_2 = Commodity(
            application,
            product_line_suffix='82',
            commodity_code='1211000000',
            indents=1,
        )
        commodity_3 = Commodity(
            application,
            product_line_suffix='80',
            commodity_code='1211110000',
            indents=2
        )
        commodity_4 = Commodity(
            application,
            product_line_suffix='80',
            commodity_code='1211111100',
            indents=3
        )
        commodity_5 = Commodity(
            application,
            product_line_suffix='80',
            commodity_code='1211111111',
            indents=4
        )
        commodity_5.assigned = True
        commodity_5.suppress_row = True

        db_chapter = ChapterFactory(id=1, description='Test')
        chapter = ScheduleChapter(application, db_chapter)
        chapter.suppress_row_for_commodity([commodity_1, commodity_2, commodity_3, commodity_4, commodity_5], 4)
        assert commodity_5.prevent_row_suppression is True
        assert commodity_5.suppress_row is False

    def test_suppress_row_for_commodity(self):
        application = mock.MagicMock(
            document_type=SCHEDULE,
            OUTPUT_DIR='/tmp',
        )
        commodity_1 = Commodity(
            application,
            product_line_suffix='80',
            commodity_code='1200000000',
            indents=0,
        )
        commodity_2 = Commodity(
            application,
            product_line_suffix='82',
            commodity_code='1211000000',
            indents=1,
        )
        commodity_3 = Commodity(
            application,
            product_line_suffix='80',
            commodity_code='1211110000',
            indents=2
        )
        commodity_4 = Commodity(
            application,
            product_line_suffix='80',
            commodity_code='1211111100',
            indents=3
        )
        commodity_5 = Commodity(
            application,
            product_line_suffix='80',
            commodity_code='1211111111',
            indents=4
        )
        commodity_5.suppress_row = False

        db_chapter = ChapterFactory(id=1, description='Test')
        chapter = ScheduleChapter(application, db_chapter)
        chapter.suppress_row_for_commodity([commodity_1, commodity_2, commodity_3, commodity_4, commodity_5], 4)
        assert commodity_5.prevent_row_suppression is False
        assert commodity_5.suppress_row is True

    def test_suppress_child_duty(self):
        application = mock.MagicMock(
            document_type=SCHEDULE,
            OUTPUT_DIR='/tmp',
        )
        commodity_1 = Commodity(
            application,
            product_line_suffix='80',
            commodity_code='1200000000',
            indents=0,
        )
        commodity_1.suppress_row = False
        commodity_2 = Commodity(
            application,
            product_line_suffix='82',
            commodity_code='1211000000',
            indents=1,
        )
        commodity_2.suppress_row = False
        commodity_3 = Commodity(
            application,
            product_line_suffix='80',
            commodity_code='1211110000',
            indents=2
        )
        commodity_3.suppress_row = False
        commodity_4 = Commodity(
            application,
            product_line_suffix='80',
            commodity_code='1211111100',
            indents=3
        )
        commodity_4.suppress_row = False
        commodity_5 = Commodity(
            application,
            product_line_suffix='80',
            commodity_code='1211111111',
            indents=4
        )
        commodity_5.suppress_row = False

        db_chapter = ChapterFactory(id=1, description='Test')
        chapter = ScheduleChapter(application, db_chapter)
        chapter.suppress_child_duty([commodity_1, commodity_2, commodity_3, commodity_4, commodity_5], 4)
        assert commodity_1.suppress_duty is True
        assert commodity_2.suppress_duty is True
        assert commodity_3.suppress_duty is True
        assert commodity_4.suppress_duty is True
        assert commodity_5.suppress_duty is False

    @pytest.mark.parametrize(
        'chapter_id,contains_authorised_use,expected_width_list',
        (
            (1, False, [600, 1050, 600, 2750]),
            (1, True, [600, 1050, 1100, 2250]),
            (2, False, [600, 900, 1150, 2350]),
            (2, True, [600, 900, 1150, 2350]),
            (9, False, [600, 900, 1150, 2350]),
            (10, False, [600, 900, 1150, 2350]),
            (11, False, [600, 900, 1150, 2350]),
        )
    )
    def test_get_width_list(self, chapter_id, contains_authorised_use, expected_width_list):
        application = mock.MagicMock(
            document_type=SCHEDULE,
            OUTPUT_DIR='/tmp',
        )
        db_chapter = ChapterFactory(id=chapter_id, description='Test')
        chapter = ScheduleChapter(application, db_chapter)
        chapter.contains_authorised_use = contains_authorised_use
        actual_width_list = chapter.get_width_list()
        assert expected_width_list == actual_width_list

    @pytest.mark.parametrize(
        'chapter_id,contains_authorised_use,expected_document_content',
        (
            (
                1,
                False,
                {
                    'WIDTH_CLASSIFICATION': '600',
                    'WIDTH_DUTY': '1050',
                    'WIDTH_NOTES': '600',
                    'WIDTH_DESCRIPTION': '2750'
                }
            ),
            (
                1,
                True,
                {
                    'WIDTH_CLASSIFICATION': '600',
                    'WIDTH_DUTY': '1050',
                    'WIDTH_NOTES': '1100',
                    'WIDTH_DESCRIPTION': '2250'
                }
            ),
            (
                2,
                False,
                {
                    'WIDTH_CLASSIFICATION': '600',
                    'WIDTH_DUTY': '900',
                    'WIDTH_NOTES': '1150',
                    'WIDTH_DESCRIPTION': '2350'
                }
            ),
            (
                2,
                True,
                {
                    'WIDTH_CLASSIFICATION': '600',
                    'WIDTH_DUTY': '900',
                    'WIDTH_NOTES': '1150',
                    'WIDTH_DESCRIPTION': '2350'
                }
            ),
            (
                9,
                False,
                {
                    'WIDTH_CLASSIFICATION': '600',
                    'WIDTH_DUTY': '900',
                    'WIDTH_NOTES': '1150',
                    'WIDTH_DESCRIPTION': '2350'
                }
            ),
            (
                10,
                False,
                {
                    'WIDTH_CLASSIFICATION': '600',
                    'WIDTH_DUTY': '900',
                    'WIDTH_NOTES': '1150',
                    'WIDTH_DESCRIPTION': '2350'
                }
            ),
            (
                11,
                False,
                {
                    'WIDTH_CLASSIFICATION': '600',
                    'WIDTH_DUTY': '900',
                    'WIDTH_NOTES': '1150',
                    'WIDTH_DESCRIPTION': '2350'
                }
            ),
        )
    )
    def test_get_document_content(self, chapter_id, contains_authorised_use, expected_document_content):
        application = mock.MagicMock(
            document_type=SCHEDULE,
            OUTPUT_DIR='/tmp',
        )
        db_chapter = ChapterFactory(id=chapter_id, description='Test')
        chapter = ScheduleChapter(application, db_chapter)
        chapter.contains_authorised_use = contains_authorised_use
        actual_document_content = chapter.get_document_content()
        assert expected_document_content == actual_document_content

    @pytest.mark.parametrize(
        'display_section_heading,expected_heading_dict',
        (
            (
                False,
                {
                    'CHAPTER': 'Chapter 01',
                    'HEADING': 'Test'
                }
            ),
            (
                True,
                {
                    'CHAPTER': 'Chapter 01',
                    'HEADING': 'Test',
                    'HEADINGa': 'Section I',
                    'HEADINGb': 'Test Section'
                }
            ),
        ),
    )
    def test_format_heading(self, display_section_heading, expected_heading_dict):
        application = mock.MagicMock(
            document_type=SCHEDULE,
            OUTPUT_DIR='/tmp',
        )
        db_chapter = ChapterFactory(id=1, description='Test', display_section_heading=display_section_heading)
        chapter = ScheduleChapter(application, db_chapter)
        chapter.section_numeral = 'I'
        chapter.section_title = 'Test Section'
        actual_heading_dict = chapter.format_heading()
        assert expected_heading_dict == actual_heading_dict

    def test_format_table(self):
        application = mock.MagicMock(
            document_type=SCHEDULE,
            OUTPUT_DIR='/tmp',
        )
        commodity_1 = Commodity(
            application,
            product_line_suffix='80',
            commodity_code='1200000000',
            indents=0,
        )
        commodity_2 = Commodity(
            application,
            product_line_suffix='80',
            commodity_code='1211000000',
            indents=3,
        )
        commodity_2.notes_list = ['2 notes']
        commodity_3 = Commodity(
            application,
            product_line_suffix='80',
            commodity_code='1211110000',
            indents=10
        )
        commodity_3.notes_list = ['3 notes']
        db_chapter = ChapterFactory(id=1, description='Test')
        chapter = ScheduleChapter(application, db_chapter)
        actual_table = chapter.format_table_content([commodity_1, commodity_2, commodity_3])
        assert 'commodity_list' in actual_table
        assert len(actual_table['commodity_list']) == 3
        assert set(actual_table['commodity_list'][0].keys()) == {'DUTY', 'DESCRIPTION', 'INDENT', 'COMMODITY', 'NOTES'}

        assert actual_table['commodity_list'][0]['COMMODITY'] == '1200'
        assert actual_table['commodity_list'][1]['COMMODITY'] == '1211'
        assert actual_table['commodity_list'][2]['COMMODITY'] == '1211 11'

        assert 'w:left="0"' in actual_table['commodity_list'][0]['INDENT']
        assert 'w:left="340"' in actual_table['commodity_list'][1]['INDENT']
        assert 'w:left="1134"' in actual_table['commodity_list'][2]['INDENT']

        assert actual_table['commodity_list'][0]['NOTES'] == '<w:r><w:t></w:t></w:r>'
        assert actual_table['commodity_list'][1]['NOTES'] == '<w:r><w:t>2 notes</w:t></w:r>'
        assert actual_table['commodity_list'][2]['NOTES'] == '<w:r><w:t>3 notes</w:t></w:r>'

    @mock.patch('trade_tariff_reference.documents.mfn.chapter.ScheduleChapter.create_document')
    def test_format_chapter(self, mock_create_document):
        mock_create_document.return_value = None
        application = mock.MagicMock(
            document_type=SCHEDULE,
            OUTPUT_DIR='/tmp',
        )
        db_chapter = ChapterFactory(id=1, description='Test')
        chapter = ScheduleChapter(application, db_chapter)
        chapter.format_chapter()
        assert mock_create_document.called
        assert set(mock_create_document.call_args_list[0][0][0].keys()) == {
            'CHAPTER',
            'HEADING',
            'WIDTH_CLASSIFICATION',
            'WIDTH_DESCRIPTION',
            'WIDTH_DUTY',
            'WIDTH_NOTES',
            'commodity_list'
        }

    @mock.patch('trade_tariff_reference.documents.mfn.chapter.ScheduleChapter.get_section_details')
    def test_get_duties(self, mock_get_section_details):
        mock_get_section_details.return_value = None
        component_1 = MeasureComponentFactory(
            measure_sid=1,
            duty_amount=1,
            duty_expression_id='15',
            monetary_unit_code='EUR'
        )
        SimpleCurrentMeasureFactory(
            measure_sid=component_1.measure_sid,
            measure_type_id='103',
            goods_nomenclature_item_id='0123456781',
            validity_start_date=datetime(2019, 11, 1, 0, 0),
        )
        component_2 = MeasureComponentFactory(measure_sid=2, duty_amount=2)
        SimpleCurrentMeasureFactory(
            measure_sid=component_2.measure_sid,
            measure_type_id='100',
            goods_nomenclature_item_id='012345672',
            validity_start_date=datetime(2019, 11, 1, 0, 0),
        )
        component_3 = MeasureComponentFactory(measure_sid=3, duty_amount=3)
        SimpleCurrentMeasureFactory(
            measure_sid=component_3.measure_sid,
            measure_type_id='103',
            goods_nomenclature_item_id='0123456783',
            validity_start_date=datetime(2018, 11, 1, 0, 0),
        )
        component_4 = MeasureComponentFactory(measure_sid=4, duty_amount=4)
        SimpleCurrentMeasureFactory(
            measure_sid=component_4.measure_sid,
            measure_type_id='103',
            goods_nomenclature_item_id='021111111',
            validity_start_date=datetime(2019, 11, 1, 0, 0),
        )

        application = Application(SCHEDULE)
        db_chapter = ChapterFactory(id=1, description='Test')
        chapter = ScheduleChapter(application, db_chapter)
        actual_duties = chapter.get_duties()
        assert len(actual_duties) == 1
        assert actual_duties[0].duty_amount == 1
        assert actual_duties[0].duty_string == 'MIN 1.000 €'
        assert actual_duties[0].commodity_code == '0123456781'
        assert actual_duties[0].monetary_unit_code == '€'
        assert actual_duties[0].measurement_unit_qualifier_code == ''


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

    @pytest.mark.parametrize(
        'context,force,expected_template,expected_document_xml,expected_change,raise_write_exception',
        (
            (
                {'fake': 'context'},
                True,
                'xml/mfn/document_classification.xml',
                'XML',
                {'dictionary_item_added': ["root['fake']"]},
                False,
            ),
            (
                {},
                False,
                'xml/mfn/document_classification.xml',
                None,
                {},
                False,
            ),
            (
                {'fake': 'context'},
                True,
                'xml/mfn/document_classification.xml',
                'XML',
                {},
                True,
            ),
        ),
    )
    @mock.patch('trade_tariff_reference.documents.mfn.chapter.ClassificationChapter.get_section_details')
    @mock.patch('trade_tariff_reference.documents.mfn.chapter.ClassificationChapter.get_duties')
    @mock.patch('trade_tariff_reference.documents.mfn.chapter.ClassificationChapter.write')
    @mock.patch('trade_tariff_reference.documents.mfn.chapter.render_to_string')
    def test_create_document(
        self,
        mock_render_to_string,
        mock_write,
        mock_get_duties,
        mock_get_section_details,
        context,
        force,
        expected_template,
        expected_document_xml,
        expected_change,
        raise_write_exception,
    ):
        fake_file_name = 'fake_file.txt'

        mock_get_duties.return_value = None
        mock_get_section_details.return_value = None
        mock_write.return_value = fake_file_name
        if raise_write_exception:
            mock_write.side_effect = EndpointConnectionError(endpoint_url='')

        mock_render_to_string.return_value = expected_document_xml
        application = Application(CLASSIFICATION, force=force)
        db_chapter = ChapterFactory(id=1, description='Test')
        chapter = ClassificationChapter(application, db_chapter)
        chapter.create_document(context)

        if expected_document_xml:
            mock_render_to_string.assert_called_with(expected_template, context)
            mock_write.asssert_called_with(expected_document_xml)
        else:
            assert mock_render_to_string.called is False
            assert mock_write.called is False

        if expected_change:
            document_history = ChapterDocumentHistory.objects.get(
                chapter=db_chapter
            )
            assert document_history.forced is force
            assert document_history.data == context
            assert document_history.change == expected_change
            assert document_history.remote_file_name == fake_file_name
        else:
            assert ChapterDocumentHistory.objects.filter(
                chapter=db_chapter
            ).exists() is False

    @mock.patch('trade_tariff_reference.documents.mfn.chapter.ClassificationChapter.create_document')
    def test_format_chapter(self, mock_create_document):
        mock_create_document.return_value = None
        application = mock.MagicMock(
            document_type=CLASSIFICATION,
            OUTPUT_DIR='/tmp',
        )
        db_chapter = ChapterFactory(id=1, description='Test')
        chapter = ClassificationChapter(application, db_chapter)
        chapter.format_chapter()
        assert mock_create_document.called
        assert set(mock_create_document.call_args_list[0][0][0].keys()) == {
            'WIDTH_CLASSIFICATION',
            'WIDTH_DUTY',
            'CHAPTER_NOTE_DOCUMENT',
            'commodity_list',
            'WIDTH_DESCRIPTION',
            'WIDTH_NOTES'
        }

    @pytest.mark.parametrize(
        'chapter_has_note',
        (
            True, False,
        ),
    )
    def test_get_chapter_note_content(self, chapter_has_note):
        application = mock.MagicMock(
            document_type=CLASSIFICATION,
            OUTPUT_DIR='/tmp',
        )
        db_chapter = ChapterFactory(id=1, description='Test')
        expected_note_content = {
            'CHAPTER_NOTE_DOCUMENT': ''
        }

        if chapter_has_note:
            db_chapter_note = ChapterNoteWithDocumentFactory(chapter=db_chapter)
            expected_note_content = {
                'CHAPTER_NOTE_DOCUMENT': db_chapter_note.document_check_sum
            }
        chapter = ClassificationChapter(application, db_chapter)
        actual_chapter_note_content = chapter.get_chapter_note_content()
        assert actual_chapter_note_content == expected_note_content
