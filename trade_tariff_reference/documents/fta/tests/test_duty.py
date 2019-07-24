import pytest

from trade_tariff_reference.documents.fta.duty import Duty
from trade_tariff_reference.schedule.tests.factories import AgreementFactory


pytestmark = pytest.mark.django_db


class FakeApplication:

    def __init__(self, country_profile=None, local_sivs=None, local_sivs_commodities_only=None, mfn_rate=0):
        self.local_sivs_commodities_only = local_sivs_commodities_only or []
        self.mfn_rate = mfn_rate
        self.country_profile = country_profile
        self.local_sivs = local_sivs or []
        if country_profile:
            self.agreement = AgreementFactory(country_name=country_profile)
        else:
            self.agreement = AgreementFactory()

    def get_mfn_rate(self, *args):
        return self.mfn_rate


class FakeSiv:

    def __init__(
        self,
        goods_nomenclature_item_id=None,
        validity_start_date=None,
        condition_measurement_unit_code=None,
        condition_duty_amount=None
    ):
        self.goods_nomenclature_item_id = goods_nomenclature_item_id
        self.validity_start_date = validity_start_date
        self.condition_measurement_unit_code = condition_measurement_unit_code
        self.condition_duty_amount = condition_duty_amount


def get_duty_object(
    application=None, commodity_code=None, additional_code_type_id=None, additional_code_id=None, measure_type_id=None,
    duty_expression_id=None, duty_amount=None, monetary_unit_code=None, measurement_unit_code=None,
    measurement_unit_qualifier_code=None, measure_sid=None, quota_order_number_id=None, geographical_area_id=None,
    validity_start_date=None, validity_end_date=None, reduction_indicator=None, is_siv=None,
):
    return Duty(
        application, commodity_code, additional_code_type_id, additional_code_id, measure_type_id,
        duty_expression_id, duty_amount, monetary_unit_code, measurement_unit_code, measurement_unit_qualifier_code,
        measure_sid, quota_order_number_id, geographical_area_id, validity_start_date, validity_end_date,
        reduction_indicator, is_siv
    )


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
    duty = get_duty_object()
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
            'S', 'raw sugar'
        ),
        (
            'T', 'dry lactic matter'  # of dry lactic matter
        ),
        (
            'X', 'hl'  # Hectolitre
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
    duty = get_duty_object(measurement_unit_qualifier_code=qualifier_code)
    assert duty.get_qualifier() == expected_result


@pytest.mark.parametrize(
    'duty_expression_id,duty_amount,monetary_unit_code,measurement_unit_code,'
    'measurement_unit_qualifier_code,expected_result',
    (
        (
            '', '', '', '', '', '',
        ),
        (
            '01', 100, '', '', '', '100.00%',
        ),
        (
            '01', 100, '$', '', '', '100.000 $',
        ),
        (
            '01', 100, '$', 'NAR', '', '100.000 $ / item',
        ),
        (
            '01', 100, '$', 'NAR', 'X', '100.000 $ / item / hl',
        ),
        (
            '01', 100, '$', 'NAR', 'UNKNOWN', '100.000 $ / item / ',
        ),
        (
            '15', 100, '$', 'NAR', 'E', 'MIN 100.000 $ / item / net drained wt',
        ),
        (
            '17', 100, '$', 'NAR', 'C', 'MAX 100.000 $ / item / 1 000',
        ),
        (
            '12', '', '', '', '', ' + AC',
        ),
        (
            '14', '', '', '', '', ' + ACR',
        ),
        (
            '21', '', '', '', '', ' + SD',
        ),
        (
            '25', '', '', '', '', ' + SDR',
        ),
        (
            '27', '', '', '', '', ' + FD',
        ),
        (
            '29', '', '', '', '', ' + FDR',
        ),
        (
            'UNKNOWN', '', '', '', '', '',
        ),
    ),
)
def test_get_duty_string(
    duty_expression_id,
    duty_amount,
    monetary_unit_code,
    measurement_unit_code,
    measurement_unit_qualifier_code,
    expected_result
):
    duty = get_duty_object(
        duty_expression_id=duty_expression_id,
        duty_amount=duty_amount,
        monetary_unit_code=monetary_unit_code,
        measurement_unit_code=measurement_unit_code,
        measurement_unit_qualifier_code=measurement_unit_qualifier_code,
    )
    assert duty.get_duty_string() == expected_result


@pytest.mark.parametrize(
    'duty_amount,commodity_code,country_profile,mfn_rate,local_sivs,expected_result',
    (
        (
            None, None, '', 0, [], 'Entry Price - 0.00% + Specific 100%',
        ),
        (
            10, None, '', 0, [], 'Entry Price - 0.00% + Specific 100%',
        ),
        (
            10, None, '', 2, [], 'Entry Price - 500.00% + Specific 100%',
        ),
        (
            10, '12345', 'morocco', 2, ['12345'], 'Entry Price - 500.00% + Specific 100%',
        ),
    ),
)
def test_get_siv_duty_string(duty_amount, commodity_code, country_profile, mfn_rate, local_sivs, expected_result):
    application = FakeApplication(
        country_profile=country_profile,
        mfn_rate=mfn_rate,
        local_sivs_commodities_only=local_sivs,
    )

    duty = get_duty_object(application=application, commodity_code=commodity_code, duty_amount=duty_amount, is_siv=True)
    assert duty.get_siv_duty_string() == expected_result


@pytest.mark.parametrize(
    'local_sivs,commodity_code,validity_start_date,expected_result',
    (
        (
            [], '', '', '',
        ),
        (
            [FakeSiv()], '', '', '',
        ),
        (
            [FakeSiv(goods_nomenclature_item_id='1235')], '12345', '', '',
        ),
        (
            [
                FakeSiv(),
                FakeSiv(
                    goods_nomenclature_item_id='12345',
                    validity_start_date='DATE',
                    condition_measurement_unit_code='LTR',
                    condition_duty_amount=1000
                ),
                FakeSiv(
                    goods_nomenclature_item_id='12345',
                    validity_start_date='DATE',
                    condition_measurement_unit_code='LTR',
                    condition_duty_amount=2000
                )
            ],
            '12345',
            'DATE',
            ' Rebased Price 1000 € / l',
        ),
    ),
)
def test_get_rebased_price_string(local_sivs, commodity_code, validity_start_date, expected_result):
    application = FakeApplication(
        local_sivs=local_sivs,
    )
    duty = get_duty_object(
        application=application, commodity_code=commodity_code, validity_start_date=validity_start_date
    )
    assert duty.get_rebased_price_string() == expected_result
