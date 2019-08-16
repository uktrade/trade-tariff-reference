import pytest

from trade_tariff_reference.documents.fta.quota_commodity import QuotaCommodity
from trade_tariff_reference.documents.fta.tests.test_measure import get_measure

pytestmark = pytest.mark.django_db


def test_commodity_initialise():
    commodity = QuotaCommodity(None, None)
    assert not commodity.suppress
    assert commodity.measure_list == []
    assert commodity.duty_string == ''
    assert commodity.commodity_code == ''
    assert commodity.commodity_code_formatted == ''
    assert commodity.quota_order_number_id == ''


@pytest.mark.parametrize(
    'contains_siv,is_all_full_year,is_infinite,expected_result',
    (
        (
            True, True, True, False,
        ),
        (
            False, False, False, True,
        ),
        (
            True, False, False, False,
        ),
        (
            True, True, False, False,
        ),
        (
            True, False, True, False,
        ),
        (
            False, False, True, False,
        ),
        (
            False, True, False, False,
        ),
    ),
)
def test_is_seasonal(contains_siv, is_all_full_year, is_infinite, expected_result):
    commodity = QuotaCommodity(None, None)
    assert commodity.is_seasonal(contains_siv, is_all_full_year, is_infinite) == expected_result


def test_is_entry_price_when_combined_duty_not_set():
    commodity = QuotaCommodity(None, None)
    commodity.measure_list.extend([get_measure(), get_measure()])
    assert not commodity.is_entry_price()


def test_is_entry_price_when_combined_duty_set():
    commodity = QuotaCommodity(None, None)
    entry_price_measure = get_measure()
    entry_price_measure.combined_duty = "Test that Entry Price is found"
    commodity.measure_list.extend([get_measure(), entry_price_measure, get_measure()])
    assert commodity.is_entry_price()


def test_check_for_no_restarted_measures():
    commodity = QuotaCommodity(None, None)
    first_measure = get_measure()
    first_measure.extent = 10
    second_measure = get_measure()
    second_measure.extent = 300
    commodity.measure_list.extend([first_measure, second_measure])
    assert commodity.check_for_restarted_measures() is False


def test_check_for_restarted_measures():
    commodity = QuotaCommodity(None, None)
    first_measure = get_measure()
    first_measure.extent = 65
    second_measure = get_measure()
    second_measure.extent = 300
    commodity.measure_list.extend([first_measure, second_measure])
    assert commodity.check_for_restarted_measures() is True


@pytest.mark.parametrize(
    'is_seasonal,suppress_measure_1,suppress_measure_2,expected_result',
    (
        (
            False, False, False, 'Combined duty 1Combined duty 2',
        ),
        (
            False, True, False, 'Combined duty 2',
        ),
        (
            False, False, True, 'Combined duty 1',
        ),
        (
            True, False, False, 'Combined duty 2',
        ),
        (
            True, True, False, 'Combined duty 2',
        ),
        (
            True, False, True, 'Combined duty 1',
        ),
        (
            True, True, True, '',
        ),
        (
            False, True, True, '',
        ),
    )
)
def test_get_duty_string_when_measure_is_not_suppressed(
    is_seasonal,
    suppress_measure_1,
    suppress_measure_2,
    expected_result,
):
    first_combined_duty_text = 'Combined duty 1'
    second_combined_duty_text = 'Combined duty 2'
    commodity = QuotaCommodity(None, None)
    first_measure = get_measure()
    first_measure.combined_duty = first_combined_duty_text
    first_measure.suppress = suppress_measure_1

    second_measure = get_measure()
    second_measure.combined_duty = second_combined_duty_text
    second_measure.suppress = suppress_measure_2

    commodity.measure_list.extend([first_measure, second_measure])
    assert commodity.get_duty_string(is_seasonal=is_seasonal) == expected_result


def test_suppress_if_eps_or_full_year():
    commodity = QuotaCommodity(None, None)
    first_measure = get_measure()
    first_measure.suppress = False

    second_measure = get_measure()
    second_measure.suppress = False

    third_measure = get_measure()
    third_measure.suppress = False

    commodity.measure_list.extend([first_measure, second_measure, third_measure])
    commodity.suppress_if_eps_or_full_year(False, True)
    assert first_measure.suppress is True
    assert second_measure.suppress is True
    assert third_measure.suppress is False


def test_suppress_if_eps_or_full_year_when_one_measure():
    commodity = QuotaCommodity(None, None)
    first_measure = get_measure()
    first_measure.suppress = False

    commodity.measure_list.extend([first_measure])
    commodity.suppress_if_eps_or_full_year(False, True)
    assert first_measure.suppress is False


def test_resolve_measure_when_seasonal():
    commodity = QuotaCommodity(None, None)
    first_measure = get_measure()
    first_measure.suppress = False
    first_measure.combined_duty = 'Combined duty 1'
    first_measure.extent = 100

    second_measure = get_measure()
    second_measure.suppress = False
    second_measure.combined_duty = 'Combined duty 2'
    second_measure.extent = 100

    commodity.measure_list.extend([first_measure, second_measure])
    commodity.resolve_measures()
    assert commodity.duty_string == 'Combined duty 2'


def test_resolve_measure_when_not_seasonal():
    commodity = QuotaCommodity(None, None)
    first_measure = get_measure()
    first_measure.suppress = False
    first_measure.combined_duty = 'Combined duty 1'
    first_measure.extent = 265

    second_measure = get_measure()
    second_measure.suppress = False
    second_measure.combined_duty = 'Combined duty 2'
    second_measure.extent = 100

    commodity.measure_list.extend([first_measure, second_measure])
    commodity.resolve_measures()
    assert commodity.duty_string == 'Combined duty 2'
