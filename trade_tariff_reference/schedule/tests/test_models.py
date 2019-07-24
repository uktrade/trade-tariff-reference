import pytest

from schedule.tests.factories import AgreementFactory

pytestmark = pytest.mark.django_db


def test_agreement_model():
    agreement = AgreementFactory(
        slug='israel',
        country_name='israel',
        version='2.0',
        country_codes=['IS', '2334'],
        agreement_date='2019-01-01',
    )

    agreement.refresh_from_db()
    assert agreement.exclusion_check == ''
    assert agreement.slug == 'israel'
    assert agreement.geo_ids == "'IS', '2334'"
    assert agreement.agreement_date_short == '01/01/2019'
    assert agreement.agreement_date_long == '1 January 2019'
