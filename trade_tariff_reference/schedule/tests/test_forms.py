from urllib.parse import urlencode

from django.http import QueryDict

import pytest

from trade_tariff_reference.schedule.forms import AgreementModelForm
from trade_tariff_reference.schedule.tests.factories import AgreementFactory

pytestmark = pytest.mark.django_db


def test_empty_create_agreement_form():
    form = AgreementModelForm(data={})
    assert not form.is_valid()
    expected_errors = {
        'agreement_date_day': ['This field is required.'],
        'agreement_date_month': ['This field is required.'],
        'agreement_date_year': ['This field is required.'],
        'agreement_name': ['This field is required.'],
        'country_codes': ['This field is required.'],
        'slug': ['This field is required.'],
        'version': ['This field is required.'],
    }
    assert form.errors == expected_errors


@pytest.mark.parametrize(
    'update_post_data,expected_errors',
    (
        (
            {
                'agreement_date_day': 31,
            },
            {
                'agreement_date': ['Invalid date'],
            },
        ),
        (
            {
                'country_codes': [],
            },
            {
                'country_codes': ['This field is required.'],
            },
        ),
        (
            {
                'country_codes': ['HELLO12', 'HG'],
            },
            {
                'country_codes': ['Invalid country code [HELLO12] value too long max 6.'],
            },
        ),
    ),
)
def test_update_agreement_errors(update_post_data, expected_errors):
    agreement = AgreementFactory()
    data = {
        'version': agreement.version,
        'agreement_name': agreement.agreement_name,
        'country_codes': agreement.country_codes,
        'slug': agreement.slug,
        'agreement_date_day': 1,
        'agreement_date_month': 2,
        'agreement_date_year': 2029,
    }
    data.update(update_post_data)
    qs = urlencode(data, True)
    post_data = QueryDict(qs)
    form = AgreementModelForm(post_data, instance=agreement)
    assert not form.is_valid()
    assert form.errors == expected_errors


def test_create_agreement_slug_already_exists():
    agreement = AgreementFactory()
    data = {
        'version': agreement.version,
        'agreement_name': agreement.agreement_name,
        'country_codes': agreement.country_codes,
        'slug': agreement.slug,
        'agreement_date_day': 1,
        'agreement_date_month': 2,
        'agreement_date_year': 2029,
    }
    qs = urlencode(data, True)
    post_data = QueryDict(qs)
    form = AgreementModelForm(post_data)
    assert not form.is_valid()
    assert form.errors == {
        'slug': ['Agreement with this Unique ID already exists.'],
    }
