import pytest

from trade_tariff_reference.documents.fta.duty import Duty


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
    duty = Duty(
        None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
    )
    assert duty.get_measurement_unit(abbreviation) == expected_result


@pytest.mark.parametrize(
    'qualifier_code,expected_result',
    (
        (
            'A', 'tot alc'  # Total alcohol
        ),
        (
            'C', '1 000'  # Total alcohol
        ),
        (
            'E', 'net drained wt'  # net of drained weight
        ),
        (
            'G', 'gross'  # Gross
        ),
        (
            'M', 'net dry'  # net of dry matter
        ),
        (
            'P', 'lactic matter'  # of lactic matter
        ),
        (
            'R', 'std qual'  # of the standard quality
        ),
        (
            'S', ' raw sugar'
        ),
        (
            'T', 'dry lactic matter'  # of dry lactic matter
        ),
        (
            'X', ' hl'  # Hectolitre
        ),
        (
            'Z', '% sacchar.'  # per 1% by weight of sucrose
        ),
        (
            None, '',
        ),
        (
            'HELLO', '',
        ),
    ),
)
def test_get_qualifier(qualifier_code, expected_result):
    duty = Duty(
        None, None, None, None, None, None, None, None, None, qualifier_code, None, None, None, None, None, None, None,
    )
    assert duty.get_qualifier() == expected_result
