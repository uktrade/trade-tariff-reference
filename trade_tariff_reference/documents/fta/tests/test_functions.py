import pytest

from trade_tariff_reference.documents.fta import functions


@pytest.mark.parametrize(
    'abbreviation,expected_result',
    (
        (
            'TNE', 'tonne'
        ),
        (
            'HELLO', 'HELLO'
        ),
        (
            None, None
        ),
        (
            'ASV', '% vol'
        ),
        (
            'DTN', '100 kg'
        ),
        (
            'HMT', '100 m'
        ),
        (
            'KGM', 'kg'
        ),
        (
            'MWH', '1,000 kWh'
        ),
        (
            'NCL', 'ce/el'
        ),
        (
            'LPA', 'l alc. 100%'
        ),
    ),
)
def test_get_measurement_unit(abbreviation, expected_result):
    assert functions.get_measurement_unit(abbreviation) == expected_result


@pytest.mark.parametrize(
    'value,expected_result',
    (
        (1, '1'),
        (None, ''),
        (True, 'True'),
        ('hello', 'hello'),
        (f'{0:1}', '0')
    ),
)
def test_mstr(value, expected_result):
    assert functions.mstr(value) == expected_result


@pytest.mark.parametrize(
    'value,expected_result',
    (
        (1, 1),
        (None, 0),
        (True, 1),
        ('hello', 0),
        (f'{0:1}', 0)
    ),
)
def test_mnum(value, expected_result):
    assert functions.mnum(value) == expected_result
