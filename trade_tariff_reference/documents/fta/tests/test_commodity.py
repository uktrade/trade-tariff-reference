from datetime import datetime

from freezegun import freeze_time

import pytest

from trade_tariff_reference.documents.fta.commodity import Commodity, format_commodity_code
from trade_tariff_reference.documents.fta.tests.test_measure import get_measure


pytestmark = pytest.mark.django_db


def test_commodity_initialise():
    commodity = Commodity(None)
    assert not commodity.suppress
    assert commodity.measure_list == []
    assert commodity.duty_string == ''
    assert commodity.commodity_code == ''
    assert commodity.commodity_code_formatted == ''


@pytest.mark.parametrize(
    'commodity_code,expected_result',
    (
        ('111111111122', '1111 11 11 11'),
        ('1111111111', '1111 11 11 11'),
        ('1111111100', '1111 11 11'),
        ('1111111000', '1111 11 10'),
        ('1111110000', '1111 11 00'),
        ('1111100000', '1111 10 00'),
        ('1111000000', '1111 00 00'),
        ('1110000000', '1110 00 00'),
        ('1100000000', '1100 00 00'),
        ('1000000000', '1000 00 00'),
        ('0000000000', '0000 00 00'),
        ('0000000001', '0000 00 00 01'),
        ('0000000011', '0000 00 00 11'),
        ('0000000111', '0000 00 01 11'),
        ('0000001111', '0000 00 11 11'),
        ('0000011111', '0000 01 11 11'),
        ('0000111111', '0000 11 11 11'),
        ('0001111111', '0001 11 11 11'),
        ('0011111111', '0011 11 11 11'),
        ('0111111111', '0111 11 11 11'),
        ('0000000010', '0000 00 00 10'),
    ),
)
def test_format_commodity_code(commodity_code, expected_result):
    assert format_commodity_code(commodity_code) == expected_result


@freeze_time('2019-02-01 12:00:00')
def test_is_all_full_year_when_measure_has_no_full_years():
    commodity = Commodity(None)
    commodity.measure_list.append(get_measure())
    commodity.measure_list.append(
        get_measure(
            validity_start_date=datetime.now(),
            validity_end_date=datetime(2020, 1, 1, 0, 0),
        ),
    )
    assert not commodity.is_all_full_year()


@freeze_time('2019-02-01 12:00:00')
def test_is_all_full_year_when_one_measure_has_an_end_date_of_a_year():
    commodity = Commodity(None)
    commodity.measure_list.append(
        get_measure(
            validity_start_date=datetime.now(),
            validity_end_date=datetime(2020, 2, 1, 0, 0)
        ),
    )
    assert commodity.is_all_full_year()


@freeze_time('2019-02-01 12:00:00')
def test_is_any_infinite():
    commodity = Commodity(None)
    commodity.measure_list.append(
        get_measure(
            validity_start_date=datetime.now(),
            validity_end_date=datetime(2020, 1, 1, 0, 0),
        ),
    )
    commodity.measure_list.append(get_measure())
    assert commodity.is_any_infinite()


@freeze_time('2019-02-01 12:00:00')
def test_is_any_infinite_returns_false_when_all_validate_end_dates_set():
    commodity = Commodity(None)
    commodity.measure_list.append(
        get_measure(
            validity_start_date=datetime.now(),
            validity_end_date=datetime(2020, 1, 1, 0, 0)
        ),
    )
    assert not commodity.is_any_infinite()


def test_process_single_measure_when_measure_list_empty():
    commodity = Commodity(None)
    assert commodity.process_single_measure(True) is None
    assert commodity.duty_string == ''
    assert commodity.suppress is False


def test_process_single_measure():
    commodity = Commodity(None)
    first_measure = get_measure()
    second_measure = get_measure()
    commodity.measure_list.extend([first_measure, second_measure])
    assert commodity.process_single_measure(True) is None
    assert commodity.measure_list == [first_measure, second_measure]
    assert commodity.duty_string == '<w:r><w:t></w:t></w:r>'
    assert commodity.suppress is False


@freeze_time('2019-01-01 12:00:00')
def test_process_single_measure_with_end_date_before_brexit():
    commodity = Commodity(None)
    first_measure = get_measure(
        validity_start_date=datetime.now(),
        validity_end_date=datetime(2019, 1, 2, 0, 0),
    )
    second_measure = get_measure(
        validity_start_date=datetime.now(),
        validity_end_date=datetime(2019, 1, 2, 0, 0)
    )
    commodity.measure_list.extend([first_measure, second_measure])
    assert commodity.process_single_measure(True) is None
    assert commodity.measure_list == [first_measure, second_measure]
    assert commodity.duty_string == '<w:r><w:t></w:t></w:r>'
    assert commodity.suppress is True


@freeze_time('2019-01-05 12:00:00')
def test_get_partial_period_list():
    commodity = Commodity(None)
    first_measure = get_measure(
        validity_start_date=datetime.now(),
        validity_end_date=datetime(2019, 1, 10, 0, 0),
    )
    second_measure = get_measure()
    commodity.measure_list.extend([first_measure, second_measure])
    actual_partial_list = commodity.get_partial_period_list()
    assert len(actual_partial_list) == 1
    assert actual_partial_list[0].marked is False
    assert actual_partial_list[0].validity_start_day == 5
    assert actual_partial_list[0].validity_start_month == 1


@freeze_time('2019-01-05 12:00:00')
def test_get_partial_period_list_with_no_measures():
    commodity = Commodity(None)
    actual_partial_list = commodity.get_partial_period_list()
    assert actual_partial_list == []


@freeze_time('2019-01-05 12:00:00')
def test_compare_measures_with_no_measures():
    commodity = Commodity(None)
    commodity.compare_measures()
    assert commodity.measure_list == []


@freeze_time('2019-01-05 12:00:00')
def test_compare_measures_with_one_measures():
    commodity = Commodity(None)
    measure = get_measure()
    commodity.measure_list.append(measure)
    commodity.compare_measures()
    assert commodity.measure_list == [measure]


@freeze_time('2019-01-05 12:00:00')
def test_compare_measures_with_measures():
    commodity = Commodity(None)
    measure = get_measure(
        commodity_code='12345',
        validity_start_date=datetime(2019, 1, 10, 0, 0),
        validity_end_date=datetime(2019, 1, 20, 0, 0)
    )
    second_measure = get_measure(
        commodity_code='12345',
        validity_start_date=datetime(2019, 1, 21, 0, 0),
        validity_end_date=datetime(2019, 1, 31, 0, 0)
    )
    commodity.measure_list.append(measure)
    commodity.measure_list.append(second_measure)
    commodity.compare_measures()
    assert commodity.measure_list == [measure]
    assert commodity.measure_list[0].period_end == '31/01'
    assert commodity.measure_list[0].period == '10/01 to 31/01'
    assert commodity.measure_list[0].validity_end_date == second_measure.validity_end_date
    assert commodity.measure_list[0].extent == 22


def test_resolve_measure():
    commodity = Commodity(None)
    first_measure = get_measure(
        commodity_code='12345',
        validity_start_date=datetime(2019, 1, 10, 0, 0),
        validity_end_date=datetime(2019, 1, 20, 0, 0)
    )

    first_measure.suppress = False
    first_measure.extent = 265
    first_measure.combined_duty = 'Combined duty 1'

    second_measure = get_measure(
        commodity_code='12345',
        validity_start_date=datetime(2019, 1, 21, 0, 0),
        validity_end_date=datetime(2019, 1, 31, 0, 0)
    )

    second_measure.suppress = False
    second_measure.extent = 100
    second_measure.combined_duty = 'Combined duty 2'

    commodity.measure_list.extend([first_measure, second_measure])
    commodity.resolve_measures()
    assert '<w:r><w:t>21/01 to 31/01</w:t></w:r>' in commodity.duty_string
    assert '<w:r><w:t>10/01 to 20/01</w:t></w:r>' in commodity.duty_string


def test_resolve_measure_with_one_measure():
    commodity = Commodity(None)
    first_measure = get_measure(
        commodity_code='12345',
        validity_start_date=datetime(2018, 1, 10, 0, 0),
        validity_end_date=datetime(2019, 1, 9, 0, 0)
    )

    first_measure.suppress = False
    first_measure.extent = 365
    first_measure.combined_duty = 'Combined duty 1'

    commodity.measure_list.extend([first_measure])
    commodity.resolve_measures()
    assert '<w:r><w:t>Combined duty 1</w:t></w:r>' in commodity.duty_string


@freeze_time('2019-01-05 12:00:00')
def test_resolve_measure_when_measures_are_combined():
    commodity = Commodity(None)
    measure = get_measure(
        commodity_code='12345',
        validity_start_date=datetime(2019, 1, 10, 0, 0),
        validity_end_date=datetime(2019, 1, 20, 0, 0)
    )
    measure.combined_duty = 'Duty'
    second_measure = get_measure(
        commodity_code='12345',
        validity_start_date=datetime(2019, 1, 21, 0, 0),
        validity_end_date=datetime(2019, 1, 31, 0, 0),
    )

    second_measure.combined_duty = 'Duty'
    commodity.measure_list.extend([second_measure, measure])
    commodity.resolve_measures()
    assert 'Duty' in commodity.duty_string
    assert '<w:r><w:t>10/01 to 31/01</w:t></w:r>' in commodity.duty_string
