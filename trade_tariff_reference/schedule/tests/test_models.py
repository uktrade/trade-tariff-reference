import pytest

from schedule.tests.factories import AgreementFactory

pytestmark = pytest.mark.django_db


def test_agreement_model():
    iceland_agreement = AgreementFactory(
        country_name='Iceland', country_codes=['IS'], reg_list=[], version='1.2'
    )
    assert iceland_agreement.country_name == 'Iceland'
    assert iceland_agreement.country_codes == ['IS']
    assert iceland_agreement.reg_list == []
    assert iceland_agreement.table_per_country == 1
