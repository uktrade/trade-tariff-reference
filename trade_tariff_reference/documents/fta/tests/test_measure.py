from datetime import datetime

from freezegun import freeze_time

import pytest

from trade_tariff_reference.documents.fta.application import Application
from trade_tariff_reference.documents.fta.measure import Measure
from trade_tariff_reference.documents.fta.tests.test_duty import get_duty_object
from trade_tariff_reference.schedule.tests.factories import AgreementFactory


pytestmark = pytest.mark.django_db


def get_measure(
    measure_sid=None,
    commodity_code=None,
    quota_order_number_id=None,
    validity_start_date=datetime.now(),
    validity_end_date=None,
    geographical_area_id=None,
    reduction_indicator=None
):
    return Measure(
        measure_sid,
        commodity_code,
        quota_order_number_id,
        validity_start_date,
        validity_end_date,
        geographical_area_id,
        reduction_indicator
    )


@freeze_time('2019-10-01')
def test_filtered_old_duties():
    measure = get_measure(
        validity_start_date=datetime.now(),
    )
    duties = [
        get_duty_object(
            measure_sid=1,
            validity_start_date=datetime(2018, 1, 1),
            validity_end_date=datetime(2018, 8, 31),
        ),
        get_duty_object(
            measure_sid=2,
            validity_start_date=datetime(2018, 9, 2),
            validity_end_date=datetime(2018, 12, 1),
        ),
    ]
    measure.old_duties = duties
    actual_duties = measure.filtered_old_duties()
    assert [duty.measure_sid for duty in actual_duties] == [2]


@freeze_time('2019-10-01')
def test_get_duty_string():
    measure = get_measure(
        validity_start_date=datetime.now(),
    )
    duties = [
        get_duty_object(
            measure_sid=1,
            validity_start_date=datetime(2018, 1, 1),
            validity_end_date=datetime(2018, 8, 31),
            duty_amount=1,
            duty_expression_id='01',
        ),
    ]
    actual_duty_string = measure.get_duty_string(duties)
    assert actual_duty_string == '1.00%'


@freeze_time('2019-10-01')
def test_combine_duties_with_no_old_duties():
    measure = get_measure(
        validity_start_date=datetime.now(),
    )
    duties = [
        get_duty_object(
            measure_sid=1,
            validity_start_date=datetime(2019, 1, 1),
            validity_end_date=datetime(2019, 8, 31),
            duty_expression_id='12',
        ),
        get_duty_object(
            measure_sid=2,
            validity_start_date=datetime(2019, 9, 2),
            validity_end_date=datetime(2019, 12, 1),
            duty_amount=2,
            duty_expression_id='12',
        ),
    ]
    measure.duty_list = duties
    AgreementFactory(country_name='Espana', slug='spain', country_codes=['1011'])
    application = Application(country_profile='spain')
    measure.combine_duties(application)
    assert measure.combined_duty == 'CAD - + (AC + AC) 100%'


@freeze_time('2019-10-01')
def test_combine_duties_with_old_duties():
    measure = get_measure(
        validity_start_date=datetime(2019, 11, 1),
    )
    duties = [
        get_duty_object(
            measure_sid=1,
            validity_start_date=datetime(2019, 1, 1),
            validity_end_date=datetime(2019, 8, 31),
            duty_expression_id='01',
            duty_amount=1,
        ),
        get_duty_object(
            measure_sid=2,
            validity_start_date=datetime(2019, 9, 2),
            validity_end_date=datetime(2019, 12, 1),
            duty_amount=2,
            duty_expression_id='01',
        ),
    ]
    old_duties = [
        get_duty_object(
            measure_sid=1,
            validity_start_date=datetime(2018, 1, 1),
            validity_end_date=datetime(2018, 8, 31),
            duty_expression_id='01',
            duty_amount=4,
        ),
        get_duty_object(
            measure_sid=2,
            validity_start_date=datetime(2018, 9, 2),
            validity_end_date=datetime(2018, 12, 1),
            duty_amount=4,
            duty_expression_id='01',
        ),
    ]
    measure.duty_list = duties
    measure.old_duties = old_duties
    AgreementFactory(country_name='Espana', slug='spain', country_codes=['1011'])
    application = Application(country_profile='spain')
    measure.combine_duties(application)
    assert measure.combined_duty == '4.00%'
