import datetime
from datetime import timezone
from unittest import mock

from override_storage import override_storage

import pytest

from trade_tariff_reference.documents.exceptions import CountryProfileError
from trade_tariff_reference.documents.fta.application import Application
from trade_tariff_reference.documents.fta.mfn_duty import MfnDuty
from trade_tariff_reference.schedule.models import DocumentStatus
from trade_tariff_reference.schedule.tests.factories import AgreementFactory
from trade_tariff_reference.tariff.models import MeursingComponents
from trade_tariff_reference.tariff.tests.factories import (
    MeasureConditionComponentFactory,
    MeasureConditionFactory,
    MeasureFactory,
    MeursingComponentsFactory,
)


pytestmark = pytest.mark.django_db


@pytest.fixture
def create_meursing_components():
    MeursingComponentsFactory(duty_amount=5, geographical_area_id='1011', reduction_indicator=3)
    MeursingComponentsFactory(duty_amount=15, geographical_area_id='1011', reduction_indicator=3)
    MeursingComponentsFactory(duty_amount=10, geographical_area_id='2000', reduction_indicator=2)
    MeursingComponentsFactory(duty_amount=30, geographical_area_id='2000', reduction_indicator=2)
    MeursingComponentsFactory(duty_amount=20, geographical_area_id='2000', reduction_indicator=1)


def get_mfn_siv_product(
    goods_nomenclature_item_id,
    duty_amount=100,
    condition_code='V',
    duty_expression_id='01',
    geographical_area_id='1011',
    start_date='2019-05-01 01:00:00',
    measure_type_id=103,
    measure_quota_number=10,
    reduction_indicator=5,
    measure_status='published',
    measure_condition_status='published',
    measure_condition_component_status='published',
):
    start_date_object = datetime.datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
    start_date_object = start_date_object.replace(tzinfo=timezone.utc)

    measure = MeasureFactory(
        goods_nomenclature_item_id=goods_nomenclature_item_id,
        validity_start_date=start_date_object,
        validity_end_date=datetime.datetime(2019, 4, 2, 1, 0, 0, tzinfo=timezone.utc),
        measure_type_id=measure_type_id,
        geographical_area_id=geographical_area_id,
        quota_order_number_id=measure_quota_number,
        reduction_indicator=reduction_indicator,
        status=measure_status,
    )
    measure_condition = MeasureConditionFactory(
        measure_sid=measure.measure_sid,
        condition_code=condition_code,
        status=measure_condition_status,
    )
    MeasureConditionComponentFactory(
        measure_condition_sid=measure_condition.measure_condition_sid,
        duty_expression_id=duty_expression_id,
        duty_amount=duty_amount,
        status=measure_condition_component_status,
    )
    return measure


def get_application(country_profile):
    AgreementFactory(country_name=country_profile, slug=country_profile)
    return Application(country_profile)


def test_get_meursing_components(create_meursing_components):
    assert MeursingComponents.objects.count() == 5
    application = get_application('israel')
    assert application.get_meursing_components() == float(10)


def test_get_meursing_percentage(create_meursing_components):
    application = get_application('israel')
    actual_percentage = application.get_meursing_percentage(2, '2000')
    assert actual_percentage == 200


def test_get_meursing_percentage_when_erga_omnes_average_none():
    application = get_application('israel')
    actual_percentage = application.get_meursing_percentage(2, '2000')
    assert actual_percentage == 100


def test_get_meursing_percentage_when_reduced_average_is_none(create_meursing_components):
    application = get_application('israel')
    actual_percentage = application.get_meursing_percentage(2, '2000')
    assert actual_percentage == 200


@pytest.mark.parametrize(
    'mfn_list,expected_rate',
    (
        (
            [],
            0
        ),
        (
            [MfnDuty(None, 1, None, None)],
            0
        ),
        (
            [
                MfnDuty('1234567800', 100, '2019-02-01 01:00:00', None),
                MfnDuty('1234567800', 200, '2019-01-01 01:00:00', None),
                MfnDuty('1234560000', 300, '2019-01-01 01:00:00', None),
                MfnDuty('1234567890', 150, '2019-01-01 01:00:00', None),
            ],
            150
        ),
        (
            [
                MfnDuty('1234567800', 100, '2019-02-01 01:00:00', None),
                MfnDuty('1234567800', 200, '2019-01-01 01:00:00', None),
                MfnDuty('1234560000', 300, '2019-01-01 01:00:00', None),
            ],
            200
        ),
        (
            [
                MfnDuty('1234567800', 100, '2019-02-01 01:00:00', None),
                MfnDuty('1234560000', 300, '2019-01-01 01:00:00', None),
            ],
            300
        ),

    ),
)
def test_get_mfn_rate(mfn_list, expected_rate):
    application = get_application('israel')
    application.mfn_list = mfn_list
    actual_rate = application.get_mfn_rate('1234567890', '2019-01-01 01:00:00')
    assert actual_rate == expected_rate


def test_get_mfns_for_siv_products_when_no_products():
    application = get_application('israel')
    application.get_mfns_for_siv_products()
    assert application.mfn_list == []


def test_get_mfns_for_siv_products_with_products():
    expected_measure = get_mfn_siv_product(1234, duty_amount=200)
    get_mfn_siv_product(1235, geographical_area_id='1021')
    get_mfn_siv_product(1236, duty_expression_id='02')
    get_mfn_siv_product(1237, condition_code='C')
    get_mfn_siv_product(1238, start_date='2017-01-01 01:00:00')
    get_mfn_siv_product(1239, duty_amount=300, measure_status='awaiting approval')
    get_mfn_siv_product(1240, duty_amount=300, measure_condition_status='awaiting approval')
    get_mfn_siv_product(1241, duty_amount=300, measure_condition_component_status='awaiting approval')

    application = get_application('israel')
    application.get_mfns_for_siv_products()
    assert len(application.mfn_list) == 1
    actual_mfn_duty = application.mfn_list[0]
    assert actual_mfn_duty.commodity_code == str(expected_measure.goods_nomenclature_item_id)
    assert actual_mfn_duty.duty_amount == 200
    assert actual_mfn_duty.validity_start_date == datetime.datetime(2019, 5, 1, 1, 0, 0, tzinfo=timezone.utc)
    assert actual_mfn_duty.validity_end_date == datetime.datetime(2019, 4, 2, 1, 0, 0, tzinfo=timezone.utc)


def test_unknown_country_profile_raises_exception():
    with pytest.raises(CountryProfileError) as error:
        Application('israel')
    assert str(error.value) == 'Country profile does not exist'


def test_agreement_raises_error_when_no_country_codes_are_associated():
    AgreementFactory(
        slug='israel',
        country_name='israel',
        version='2.0',
        country_codes=[],
        agreement_date='2019-01-01',
    )

    with pytest.raises(CountryProfileError) as error:
        Application('israel')
    assert str(error.value) == 'Country profile has no country codes'


def test_agreement_properties_set():
    AgreementFactory(
        slug='israel',
        country_name='israel',
        version='2.0',
        country_codes=['IS', '2334'],
        agreement_date='2019-01-01',
    )
    application = Application('israel')
    assert application.agreement.slug == 'israel'
    assert application.agreement.geo_ids == "'IS', '2334'"
    assert application.agreement.agreement_date_short == '01/01/2019'
    assert application.agreement.agreement_date_long == '1 January 2019'


@override_storage()
@mock.patch('trade_tariff_reference.documents.fta.document.Document.create_document')
def test_main_with_no_quotas(mock_create_document):
    mock_create_document.return_value = None
    agreement = AgreementFactory(
        slug='israel',
        country_name='israel',
        version='2.0',
        country_codes=['IS', '2334'],
        agreement_date='2019-01-01',
        document_status=DocumentStatus.UNAVAILABLE
    )
    application = Application('israel')
    application.main()
    agreement.refresh_from_db()
    assert agreement.document_status == DocumentStatus.AVAILABLE
    assert mock_create_document.called is True
    expected_context = {
        'AGREEMENT_NAME': agreement.agreement_name,
        'VERSION': '2.0',
        'AGREEMENT_DATE': '1 January 2019',
        'AGREEMENT_DATE_SHORT': '01/01/2019',
        'COUNTRY_NAME': 'israel',
        'TARIFF_WIDTH_CLASSIFICATION': '400',
        'TARIFF_WIDTH_DUTY': '1450',
        'TARIFF_TABLE_ROWS': [],
        'WIDTH_QUOTA_NUMBER': '8',
        'WIDTH_ORIGIN_QUOTA': '7',
        'WIDTH_COMMODITY_CODE': '11',
        'WIDTH_PREFERENTIAL_QUOTA_DUTY_RATE': '22',
        'WIDTH_QUOTA_VOLUME': '16',
        'WIDTH_QUOTA_OPEN_DATE': '10',
        'WIDTH_QUOTA_CLOSE_DATE': '10',
        'WIDTH_2019_QUOTA_VOLUME': '16',
        'QUOTA_TABLE_ROWS': [],
        'HAS_QUOTAS': False
    }

    mock_create_document.assert_called_with(expected_context)
