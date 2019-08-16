from datetime import datetime, timezone
from unittest import mock

import pytest

from trade_tariff_reference.documents.fta.application import Application
from trade_tariff_reference.documents.fta.document import Document
from trade_tariff_reference.documents.fta.tests.test_application import get_mfn_siv_product
from trade_tariff_reference.schedule.tests.factories import AgreementFactory
from trade_tariff_reference.tariff.tests.factories import CurrentMeasureFactory, GoodsNomenclatureFactory


pytestmark = pytest.mark.django_db


def test_document_initialise():
    application = mock.MagicMock(country_name='spain')
    document = Document(application)
    document.application.get_mfns_for_siv_products.assert_called_with()
    assert document.footnote_list == []
    assert document.balance_dict == {}
    assert document.duty_list == []
    assert document.supplementary_unit_list == []
    assert document.seasonal_records == 0
    assert document.wide_duty is False


def test_check_for_quotas_is_false():
    CurrentMeasureFactory(measure_type_id='140', geographical_area_id='1234', ordernumber=1)
    CurrentMeasureFactory(measure_type_id='143', geographical_area_id='1235', ordernumber=2)
    AgreementFactory(country_name='Espana', slug='spain', country_codes=['1234'])
    application = Application(country_profile='spain')
    document = Document(application)
    assert document.check_for_quotas() is False


def test_check_for_quotas_is_true():
    CurrentMeasureFactory(measure_type_id='143', geographical_area_id='1234', ordernumber=1)
    AgreementFactory(country_name='Espana', slug='spain', country_codes=['1234'])
    application = Application(country_profile='spain')
    document = Document(application)
    assert document.check_for_quotas() is True


@pytest.mark.parametrize(
    'instrument_type,expected_result',
    (
        ('hello', "'143', '146'"),
        ('preferences', "'142', '145'"),
    )
)
def test_get_measure_type_list_for_instrument_type(instrument_type, expected_result):
    application = mock.MagicMock(country_name='spain')
    document = Document(application)
    actual_result = document.get_measure_type_list_for_instrument_type(instrument_type)
    assert actual_result == expected_result


def test_get_measure_conditions():
    duty_amount = 200
    measure = get_mfn_siv_product(1, duty_amount=duty_amount)
    AgreementFactory(country_name='Espana', slug='spain', country_codes=['1011'])
    application = Application(country_profile='spain')
    document = Document(application)
    actual_result = document.get_measure_conditions("'103'")
    assert len(actual_result) == 1

    assert measure.measure_sid in actual_result
    actual_measure_condition = actual_result[measure.measure_sid]
    assert actual_measure_condition.condition_duty_amount == duty_amount
    assert actual_measure_condition.measure_sid == measure.measure_sid
    assert actual_measure_condition.measure_condition_sid == 0
    assert actual_measure_condition.component_sequence_number == 1
    assert actual_measure_condition.condition_code == 'V'


def test_get_measure_list():
    measure = get_mfn_siv_product(1, geographical_area_id='1011', measure_type_id='143')
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
    AgreementFactory(country_name='Espana', slug='spain', country_codes=['1011'])
    application = Application(country_profile='spain')
    document = Document(application)
    actual_measure_list = document.get_measure_list()
    assert len(actual_measure_list) == 1
    actual_measure = actual_measure_list[0]
    assert actual_measure.commodity_code == str(current_measure.goods_nomenclature_item_id)
    assert actual_measure.measure_sid == current_measure.measure_sid
    assert actual_measure.quota_order_number_id == str(current_measure.ordernumber)
    assert actual_measure.validity_start_date == current_measure.validity_start_date
    assert actual_measure.validity_end_date == current_measure.validity_end_date
    assert actual_measure.geographical_area_id == current_measure.geographical_area_id
    assert actual_measure.reduction_indicator == current_measure.reduction_indicator


def test_get_quota_measures():
    measure = get_mfn_siv_product(1, geographical_area_id='1011', measure_type_id='143')
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
    AgreementFactory(country_name='Espana', slug='spain', country_codes=['1011'])
    application = Application(country_profile='spain')
    document = Document(application)
    document.get_quota_measures()
    actual_measure_list = document.measure_list
    assert len(actual_measure_list) == 1, 'Not the correct things to assert'
    actual_measure = actual_measure_list[0]
    assert actual_measure.commodity_code == str(current_measure.goods_nomenclature_item_id)
    assert actual_measure.measure_sid == current_measure.measure_sid
    assert actual_measure.quota_order_number_id == str(current_measure.ordernumber)
    assert actual_measure.validity_start_date == current_measure.validity_start_date
    assert actual_measure.validity_end_date == current_measure.validity_end_date
    assert actual_measure.geographical_area_id == current_measure.geographical_area_id
    assert actual_measure.reduction_indicator == current_measure.reduction_indicator


def test_get_duties():
    measure = get_mfn_siv_product(1, geographical_area_id='1011', measure_type_id='143')
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
    AgreementFactory(country_name='Espana', slug='spain', country_codes=['1011'])
    application = Application(country_profile='spain')

    GoodsNomenclatureFactory(goods_nomenclature_item_id=current_measure.goods_nomenclature_item_id)
    document = Document(application)
    actual_duties = list(document._get_duties("'143', '146'"))
    assert len(actual_duties) == 1
    actual_duty = actual_duties[0]

    expected_duty = {
        'additional_code_id': None,
        'additional_code_type_id': None,
        'duty_amount': None,
        'duty_expression_id': None,
        'geographical_area_id': '1011',
        'goods_nomenclature_item_id': '1',
        'measure_sid': current_measure.measure_sid,
        'measure_type_id': '143',
        'measurement_unit_code': None,
        'measurement_unit_qualifier_code': None,
        'monetary_unit_code': None,
        'ordernumber': '10',
        'reduction_indicator': 5,
        'validity_end_date': datetime(2019, 4, 2, 1, 0, tzinfo=timezone.utc),
        'validity_start_date': datetime(2019, 5, 1, 1, 0, tzinfo=timezone.utc)
    }
    assert actual_duty == expected_duty
