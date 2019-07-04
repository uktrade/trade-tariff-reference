import pytest

from trade_tariff_reference.documents.fta.quota_definition import QuotaDefinition


def get_quota_definition(
    quota_definition_sid=None,
    quota_order_number_id=None,
    validity_start_date=None,
    validity_end_date=None,
    quota_order_number_sid=None,
    volume=None,
    initial_volume=None,
    measurement_unit_code=None,
    maximum_precision=None,
    critical_state=None,
    critical_threshold=None,
    monetary_unit_code=None,
    measurement_unit_qualifier_code=None
):
    return QuotaDefinition(
        quota_definition_sid,
        quota_order_number_id,
        validity_start_date,
        validity_end_date,
        quota_order_number_sid,
        volume,
        initial_volume,
        measurement_unit_code,
        maximum_precision,
        critical_state,
        critical_threshold,
        monetary_unit_code,
        measurement_unit_qualifier_code
    )


@pytest.mark.parametrize(
    'volume,measurement_unit_code,measurement_unit_qualifier_code,expected_result',
    (
        (
            1234, 'GRM', None, '1,234 g',
        ),
        (
            1234, 'GRM', 'item    ', '1,234 g item',
        ),
        (
            1234, None, None, '1,234',
        ),
    ),
)
def test_format_volume(volume, measurement_unit_code, measurement_unit_qualifier_code, expected_result):
    quota_definition = get_quota_definition(
        measurement_unit_code=measurement_unit_code,
        measurement_unit_qualifier_code=measurement_unit_qualifier_code,
    )
    assert quota_definition.format_volume(volume) == expected_result
