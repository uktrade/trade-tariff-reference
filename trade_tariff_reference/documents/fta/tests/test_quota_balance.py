import pytest

from trade_tariff_reference.documents.fta.quota_balance import QuotaBalance


def get_quota_balance(
    quota_order_number_id=None,
    country=None,
    method=None,
    y1_balance=None,
    yx_balance=None,
    yx_start='20/1/2010',
    measurement_unit_code='',
    origin_quota=None,
    addendum='',
    scope=''
):
    return QuotaBalance(
        quota_order_number_id,
        country,
        method,
        y1_balance,
        yx_balance,
        yx_start,
        measurement_unit_code,
        origin_quota,
        addendum,
        scope
    )


@pytest.mark.parametrize(
    'yx_start,expected_start_date,expected_end_date',
    (
        ('1/1/2019', '2019-03-29 00:00:00', '2019-12-31 00:00:00'),
        ('1/3/2018', '2019-03-29 00:00:00', '2019-12-31 00:00:00'),
        ('1/4/2018', '2018-04-01 00:00:00', '2019-03-31 00:00:00'),
        # MPP: TODO not sure of the above result. Should the function check the year is 2019
        ('1/8/2019', '2019-08-01 00:00:00', '2020-07-31 00:00:00'),
    ),

)
def test_add_year(yx_start, expected_start_date, expected_end_date):
    quota_balance = get_quota_balance(yx_start=yx_start)
    assert str(quota_balance.validity_start_date_2019) == expected_start_date
    assert str(quota_balance.validity_end_date_2019) == expected_end_date


@pytest.mark.parametrize(
    'origin_quota,expected_result',
    (
        ('N', 'N'),
        ('Y', 'Yes'),
        ('Hello', 'Hello'),
        (None, None),
        ('', ''),
    ),
)
def test_origin_quota(origin_quota, expected_result):
    assert get_quota_balance(origin_quota=origin_quota).origin_quota == expected_result


@pytest.mark.parametrize(
    'date,',
    (
        None, '', 1, 'Hello',
    )
)
def test_add_year_returns_none_when_error_is_thrown(date):
    quota_balance = get_quota_balance()
    assert not quota_balance.add_year(date)
