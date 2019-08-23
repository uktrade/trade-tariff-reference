import pytest

from trade_tariff_reference.documents.mfn.duty import Duty


def test_empty_initialise():
    duty = Duty()
    assert duty.commodity_code == ""
    assert duty.additional_code_type_id == ""
    assert duty.additional_code_id == ""
    assert duty.measure_type_id == ""
    assert duty.duty_expression_id == ""
    assert duty.duty_amount == 0
    assert duty.monetary_unit_code == ""
    assert duty.measurement_unit_code == ""
    assert duty.measurement_unit_qualifier_code == ""
    assert duty.measure_sid == 0
    assert duty.duty_string == ""
    assert duty.measure_type_description == ""


def test_initialise():
    duty = Duty(
        commodity_code=1,
        additional_code_type_id=2,
        additional_code_id=3,
        measure_type_id=4,
        duty_expression_id=5,
        duty_amount=6,
        monetary_unit_code=7,
        measurement_unit_code=8,
        measurement_unit_qualifier_code=9,
        measure_sid=10,
    )
    assert duty.commodity_code == "1"
    assert duty.additional_code_type_id == "2"
    assert duty.additional_code_id == "3"
    assert duty.measure_type_id == "4"
    assert duty.duty_expression_id == "5"
    assert duty.duty_amount == 6
    assert duty.monetary_unit_code == "7"
    assert duty.measurement_unit_code == "8"
    assert duty.measurement_unit_qualifier_code == "9"
    assert duty.measure_sid == 10
    assert duty.duty_string == ""
    assert duty.measure_type_description == ""


@pytest.mark.parametrize(
    'duty_expression_id,duty_amount,monetary_unit_code,measurement_unit_code,'
    'measurement_unit_qualifier_code,expected_duty_string',
    (
        (
            '01', 1, 'GBP', 'MTK', 'A', '1.000 GBP / m2 / tot alc'
        ),
        (
            '01', 1, None, 'MTK', 'A', '1.0%'
        ),
        (
            '04', 1, 'GBP', 'MTK', 'A', '+ 1.000 GBP / m2 / tot alc'
        ),
        (
            '04', 1, None, 'MTK', 'A', '+ 1.0%'
        ),
        (
            '19', 1, 'GBP', 'MTK', 'A', '+ 1.000 GBP / m2 / tot alc'
        ),
        (
            '19', 1, None, 'MTK', 'A', '+ 1.0%'
        ),
        (
            '20', 1, 'GBP', 'MTK', 'A', '+ 1.000 GBP / m2 / tot alc'
        ),
        (
            '20', 1, None, 'MTK', 'A', '+ 1.0%'
        ),
        (
            '12', 1, 'GBP', 'MTK', 'A', ' + AC'
        ),
        (
            '12', 1, None, 'MTK', 'A', ' + AC'
        ),
        (
            '15', 1, 'GBP', 'MTK', 'A', 'MIN 1.000 GBP / m2 / tot alc'
        ),
        (
            '15', 1, None, 'MTK', 'A', 'MIN 1.0%'
        ),
        (
            '17', 1, 'GBP', 'MTK', 'A', 'MAX 1.000 GBP / m2 / tot alc'
        ),
        (
            '17', 1, None, 'MTK', 'A', 'MAX 1.0%'
        ),
        (
            '21', 1, 'GBP', 'MTK', 'A', ' + SD'
        ),
        (
            '21', 1, None, 'MTK', 'A', ' + SD'
        ),
        (
            '27', 1, 'GBP', 'MTK', 'A', ' + FD'
        ),
        (
            '27', 1, None, 'MTK', 'A', ' + FD'
        ),
        (
            '30', 1, 'GBP', 'MTK', 'A', ''
        ),
        (
            '30', 1, None, 'MTK', 'A', ''
        ),
    ),
)
def test_get_duty_string(
    duty_expression_id,
    duty_amount,
    monetary_unit_code,
    measurement_unit_code,
    measurement_unit_qualifier_code,
    expected_duty_string
):
    duty = Duty(
        duty_expression_id=duty_expression_id,
        duty_amount=duty_amount,
        monetary_unit_code=monetary_unit_code,
        measurement_unit_code=measurement_unit_code,
        measurement_unit_qualifier_code=measurement_unit_qualifier_code,
    )
    assert duty.duty_string == expected_duty_string


@pytest.mark.parametrize(
    'duty_expression_id,expected_abbreviation',
    (
        (
            '01', None,
        ),
        (
            '12', ' + AC',
        ),
        (
            '21', ' + SD',
        ),
        (
            '27', ' + FD',
        ),
        (
            '46', None,
        ),
    ),
)
def test_get_duty_string_additional_abbreviation(duty_expression_id, expected_abbreviation):
    duty = Duty(
        duty_expression_id=duty_expression_id,
    )
    assert duty.get_duty_string_additional_abbreviation() == expected_abbreviation


@pytest.mark.parametrize(
    'duty_expression_id,expected_result',
    (
        (
            '04', '+ ',
        ),
        (
            '19', '+ ',
        ),
        (
            '20', '+ ',
        ),
        (
            '15', 'MIN ',
        ),
        (
            '17', 'MAX ',
        ),
        (
            '43', '',
        ),
        (
            '01', '',
        ),
    ),
)
def test_get_duty_prefix(duty_expression_id, expected_result):
    duty = Duty(
        duty_expression_id=duty_expression_id,
    )
    assert duty.get_duty_string_prefix() == expected_result


@pytest.mark.parametrize(
    'measurement_unit_code,measurement_unit_qualifier_code,expected_result',
    (
        (
            '', '', '',
        ),
        (
            'Hello', '', ' / Hello',
        ),
        (
            'Hello', 'Goodbye', ' / Hello / ',
        ),
        (
            'Hello', 'G', ' / Hello / gross',
        ),
        (
            '', 'G', '',
        ),
        (
            'KGM', 'G', ' / kg / gross',
        ),
    ),
)
def test_get_duty_suffix(measurement_unit_code, measurement_unit_qualifier_code, expected_result):
    duty = Duty(
        measurement_unit_code=measurement_unit_code,
        measurement_unit_qualifier_code=measurement_unit_qualifier_code,
    )
    assert duty.get_duty_string_suffix() == expected_result
