from unittest import mock

import pytest

from trade_tariff_reference.documents.fta.application import Application
from trade_tariff_reference.documents.fta.document import Document
from trade_tariff_reference.documents.fta.tests.test_application import get_mfn_siv_product
from trade_tariff_reference.schedule.tests.factories import AgreementFactory
from trade_tariff_reference.tariff.tests.factories import CurrentMeasureFactory


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

    actual_measure_condition = actual_result[0]
    assert actual_measure_condition.condition_duty_amount == duty_amount
    assert actual_measure_condition.measure_sid == measure.measure_sid
    assert actual_measure_condition.measure_condition_sid == 0
    assert actual_measure_condition.component_sequence_number == 1
    assert actual_measure_condition.condition_code == 'V'
