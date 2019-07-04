import pytest

from trade_tariff_reference.documents.fta.quota_commodity import QuotaCommodity


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
    quota_commodity = QuotaCommodity(commodity_code, None)
    assert quota_commodity.format_commodity_code() == expected_result


def test_resolve_measures():
    assert 1 == 2
