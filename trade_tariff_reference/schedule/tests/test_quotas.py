import pytest

from trade_tariff_reference.schedule.quotas import (
    dict_merge,
    process_csv_input,
    process_quotas,
)


@pytest.mark.parametrize(
    'is_origin_quota,is_licensed_quota,expected_result',
    (
        (
            False,
            False,
            {
                '10000': {
                    'scope': '500, apples',
                },
                '33030': {
                    'scope': 'hello',
                },
            },
        ),
        (
            True,
            False,
            {
                '10000': {
                    'scope': '500, apples',
                    'is_origin_quota': True,
                },
                '33030': {
                    'scope': 'hello',
                    'is_origin_quota': True,
                },
            },
        ),
        (
            False,
            True,
            {
                '10000': {
                    'scope': '500, apples',
                    'quota_type': 'L',
                },
                '33030': {
                    'scope': 'hello',
                    'quota_type': 'L',
                },
            },
        ),
        (
            True,
            True,
            {
                '10000': {
                    'scope': '500, apples',
                    'quota_type': 'L',
                    'is_origin_quota': True,
                },
                '33030': {
                    'scope': 'hello',
                    'quota_type': 'L',
                    'is_origin_quota': True,
                },
            },
        ),
    ),
)
def test_process_csv_input(is_origin_quota, is_licensed_quota, expected_result):
    test_string = '10000,"500, apples"\r\n33030,hello\r\n,goodbye'
    actual_result = process_csv_input(
        test_string, ['quota_order_number_id', 'scope'],
        is_origin_quota=is_origin_quota,
        is_licensed_quota=is_licensed_quota,
    )
    assert actual_result == expected_result


def test_dict_merge():
    original_dict = {
        '1': {'prop1': 'hello'},
        '2': {'prop1': 'hi'},
    }
    merge_dict = {
        '1': {'prop2': 'goodbye'},
        '3': {'prop3': 'bye'},
    }
    actual_result = dict_merge(original_dict, merge_dict)
    assert actual_result == {
            '1': {'prop1': 'hello', 'prop2': 'goodbye'},
            '2': {'prop1': 'hi'},
            '3': {'prop3': 'bye'},
    }


def test_process_quotas_with_empty_data():
    actual_result = process_quotas({})
    assert actual_result == {}


def test_process_origin_quotas():
    data = {'origin_quotas': '123\r\n456\r\n890\r\n\r\n'}
    actual_result = process_quotas(data)
    assert actual_result == {
        '123': {'is_origin_quota': True},
        '456': {'is_origin_quota': True},
        '890': {'is_origin_quota': True},
    }


def test_process_licensed_quotas():
    data = {'licensed_quotas': '123,1,A\r\n456,2,B\r\n890,,C\r\n\r\n'}
    actual_result = process_quotas(data)
    assert actual_result == {
        '123': {'quota_type': 'L', 'measurement_unit_code': 'A', 'opening_balance': '1'},
        '456': {'quota_type': 'L', 'measurement_unit_code': 'B', 'opening_balance': '2'},
        '890': {'quota_type': 'L', 'measurement_unit_code': 'C', 'opening_balance': ''},
    }


def test_process_scope_quotas():
    data = {'scope_quotas': '123,scope1\r\n456,scope2\r\n890,scope3\r\n\r\n'}
    actual_result = process_quotas(data)
    assert actual_result == {
        '123': {'scope': 'scope1'},
        '456': {'scope': 'scope2'},
        '890': {'scope': 'scope3'},
    }


def test_process_staging_quotas():
    data = {'staging_quotas': '123,add1\r\n456,add2\r\n890,add3\r\n\r\n'}
    actual_result = process_quotas(data)
    assert actual_result == {
        '123': {'addendum': 'add1'},
        '456': {'addendum': 'add2'},
        '890': {'addendum': 'add3'},
    }
