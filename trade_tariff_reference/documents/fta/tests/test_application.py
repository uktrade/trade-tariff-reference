import pytest

from unittest import mock
import datetime
from datetime import timezone

from trade_tariff_reference.documents.fta.application import Application
from trade_tariff_reference.tariff.tests.factories import (
    MeursingComponentsFactory,
    MeasureFactory,
    MeasureConditionFactory,
    MeasureConditionComponentFactory,
)
from trade_tariff_reference.tariff.models import MeursingComponents
from documents.fta.mfn_duty import MfnDuty
from documents.fta.exceptions import CountryProfileError


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
    start_date='2019-01-01 01:00:00',
    measure_type_id=103
):
    start_date_object = datetime.datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
    start_date_object = start_date_object.replace(tzinfo=timezone.utc)

    measure = MeasureFactory(
        goods_nomenclature_item_id=goods_nomenclature_item_id,
        validity_start_date=start_date_object,
        validity_end_date=datetime.datetime(2019, 1, 2, 1, 0, 0, tzinfo=timezone.utc),
        measure_type_id=measure_type_id,
        geographical_area_id=geographical_area_id
    )
    measure_condition = MeasureConditionFactory(
        measure_sid=measure.measure_sid,
        condition_code=condition_code,
    )
    MeasureConditionComponentFactory(
        measure_condition_sid=measure_condition.measure_condition_sid,
        duty_expression_id=duty_expression_id,
        duty_amount=duty_amount,
    )
    return measure


def get_application(country_profile):
    with mock.patch('trade_tariff_reference.documents.fta.application.Application._get_config') as mock_get_config:
        mock_get_config.return_value = None
        return Application(country_profile)


@pytest.mark.xfail
def test_get_section_chapters():
    application = get_application('israel')
    application.get_sections_chapters()
    # MPP: TODO if required add Sections and ChaptersSections models and link to GoodsNomenclature
    assert application.section_chapter_list == []


def test_get_meursing_components(create_meursing_components):
    assert MeursingComponents.objects.count() == 5
    application = get_application('israel')
    application.get_meursing_components()
    assert application.erga_omnes_average == float(10)


def test_get_meursing_percentage(create_meursing_components):
    application = get_application('israel')
    application.get_meursing_components()
    actual_percentage = application.get_meursing_percentage(2, '2000')
    assert actual_percentage == 200


def test_get_meursing_percentage_when_erga_omnes_average_none():
    application = get_application('israel')
    actual_percentage = application.get_meursing_percentage(2, '2000')
    assert actual_percentage == 100


def test_get_meursing_percentage_when_reduced_average_is_none(create_meursing_components):
    application = get_application('israel')
    actual_percentage = application.get_meursing_percentage(0, '2000')
    assert actual_percentage == 100


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

    application = get_application('israel')
    application.get_mfns_for_siv_products()
    assert len(application.mfn_list) == 1
    actual_mfn_duty = application.mfn_list[0]
    assert actual_mfn_duty.commodity_code == str(expected_measure.goods_nomenclature_item_id)
    assert actual_mfn_duty.duty_amount == 200
    assert actual_mfn_duty.validity_start_date == datetime.datetime(2019, 1, 1, 1, 0, 0, tzinfo=timezone.utc)
    assert actual_mfn_duty.validity_end_date == datetime.datetime(2019, 1, 2, 1, 0, 0, tzinfo=timezone.utc)


def test_get_country_list_unknown_profile_raises_exception():
    application = get_application('israel')
    with pytest.raises(CountryProfileError) as error:
        application.get_country_list()
    assert str(error.value) == 'Country profile does not exist'


def test_get_country_list_profile_without_country_codes_raises_exception():
    application = get_application('israel')
    application.all_country_profiles = {'israel': {}}
    with pytest.raises(CountryProfileError) as error:
        application.get_country_list()
    assert str(error.value) == 'Country profile has no country codes'


def test_get_country_list_profile_without_exclusion_check():
    application = get_application('israel')
    application.all_country_profiles = {
        'israel': {
            'country_name': 'country',
            'version': '1.0',
            'table_per_country': 0,
            'agreement_name': 'Agreement',
            'agreement_date': '05/02/2019',
            'country_codes': []
        }
    }
    application.get_country_list()
    assert application.exclusion_check == ''


def test_get_country_list_profile():
    application = get_application('israel')
    application.all_country_profiles = {
        'israel': {
            'country_name': 'country',
            'version': '1.0',
            'table_per_country': 0,
            'agreement_name': 'Agreement',
            'agreement_date': '05/02/2019',
            'country_codes': [],
            'exclusion_check': '12345'
        }
    }
    application.get_country_list()
    assert application.exclusion_check == '12345'
    assert application.country_name == 'country'
    assert application.version == '1.0'
    assert application.agreement_name == 'Agreement'
    assert application.agreement_date_short == '05/02/2019'
    assert application.agreement_date_long == '5 February 2019'
    assert application.country_codes == []
