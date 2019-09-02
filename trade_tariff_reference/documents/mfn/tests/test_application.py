from unittest import mock

import pytest

from trade_tariff_reference.documents.fta.tests.test_application import get_mfn_siv_product
from trade_tariff_reference.documents.mfn.application import Application
from trade_tariff_reference.documents.mfn.constants import CUCUMBER_COMMODITY_CODES, SCHEDULE
from trade_tariff_reference.schedule.tests.factories import LatinTermFactory, SpecialNoteFactory
from trade_tariff_reference.tariff.tests.factories import (
    ChapterSectionFactory,
    CurrentMeasureFactory,
    GoodsNomenclatureFactory
)

pytestmark = pytest.mark.django_db


def test_initialise():
    application = Application(SCHEDULE)
    assert application.document_type == SCHEDULE
    assert application.first_chapter == 1
    assert application.last_chapter == 99
    assert application.authorised_use_list == []
    assert application.special_list == []
    assert application.section_chapter_list == []
    assert application.latin_phrases == []
    assert application.suppress_duties is False
    assert application.latin_phrases is not None


def test_get_latin_phrases():
    latin_term = LatinTermFactory()
    application = Application(SCHEDULE)
    actual_latin_phrases = application.get_latin_phrases()
    assert actual_latin_phrases == [latin_term.text]


def test_special_notes():
    special_note = SpecialNoteFactory()
    application = Application(SCHEDULE)
    actual_special_notes = application.get_special_notes()
    assert len(actual_special_notes) == 1
    assert actual_special_notes[0].commodity_code == special_note.quota_order_number_id


def test_get_authorised_use_commodities():
    measure = get_mfn_siv_product(1, geographical_area_id='1011', measure_type_id='105')
    current_measure = CurrentMeasureFactory(
        measure_sid=measure.measure_sid,
        geographical_area_id=measure.geographical_area_id,
        measure_type_id=measure.measure_type_id,
        validity_start_date=measure.validity_start_date,
        validity_end_date=measure.validity_end_date,
        ordernumber=measure.quota_order_number_id,
        goods_nomenclature_item_id=measure.goods_nomenclature_item_id,
        reduction_indicator=measure.reduction_indicator,
    )

    application = Application(SCHEDULE)
    actual_authorised_use_commodities = application.get_authorised_use_commodities()
    assert len(actual_authorised_use_commodities) == 3
    for cucumber_commodity in CUCUMBER_COMMODITY_CODES:
        assert cucumber_commodity in actual_authorised_use_commodities
    assert str(current_measure.goods_nomenclature_item_id) in actual_authorised_use_commodities


def test_get_sections_chapters():
    goods_nomeclature_without_item = GoodsNomenclatureFactory(
        id=3,
    )
    chapter_section_without_item = ChapterSectionFactory(
        goods_nomenclature_sid=goods_nomeclature_without_item.id,
        section_id=2
    )

    goods_nomeclature = GoodsNomenclatureFactory(
        id=2,
        goods_nomenclature_item_id=10
    )
    chapter_section = ChapterSectionFactory(
        goods_nomenclature_sid=goods_nomeclature.id,
        section_id=1
    )

    application = Application(SCHEDULE)
    section_chapters = application.get_sections_chapters()
    assert section_chapters == [
        [str(goods_nomeclature.goods_nomenclature_item_id), chapter_section.section_id, False],
        [None, chapter_section_without_item.section_id, False],
    ]


@mock.patch('trade_tariff_reference.documents.mfn.application.process_chapter')
def test_main(mock_process_chapter):
    mock_process_chapter.return_value = None
    application = Application(SCHEDULE, first_chapter=10, last_chapter=11)
    application.main()
    assert mock_process_chapter.call_count == 2
    mock_process_chapter.assert_any_call(application, 10)
    mock_process_chapter.assert_any_call(application, 11)
