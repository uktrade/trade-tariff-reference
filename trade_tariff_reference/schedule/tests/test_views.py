from datetime import date

from django.shortcuts import reverse

import pytest

from trade_tariff_reference.schedule.models import Agreement, ExtendedQuota
from trade_tariff_reference.schedule.tests.factories import AgreementFactory, setup_quota_data

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url,expected_template_used,expected_heading,is_fieldset',
    (
        (
            'schedule:create', 'schedule/create.html', 'Create new agreement', True,
        ),
        (
            'schedule:manage', 'schedule/manage.html', 'Manage agreement schedules', False,
        ),
    ),
)
def test_view_renders_successfully(client, url, expected_template_used, expected_heading, is_fieldset):
    uri = reverse(url)
    _assert_view_propoerties(client, uri, expected_template_used, expected_heading, is_fieldset)


def _assert_view_propoerties(client, uri, expected_template_used, expected_heading, is_fieldset):
    response = client.get(uri)
    assert response.status_code == 200
    assert expected_template_used in [template.name for template in response.templates]
    if is_fieldset:
        expected_page_title = f'<h1 class="govuk-fieldset__heading">{expected_heading}</h1>'
    else:
        expected_page_title = f'<h1 class="govuk-heading-xl govuk-!-margin-bottom-6">{expected_heading}</h1>'
    assert expected_page_title in str(response.content)


def test_view_edit_agreement_renders_successfully(client):
    agreement = AgreementFactory()
    uri = reverse('schedule:edit', kwargs={'slug': agreement.slug})
    _assert_view_propoerties(client, uri, 'schedule/create.html', 'Edit agreement', True)


def test_view_manage_extended_information_renders_successfully(client):
    origin_quota, licensed_quota, scope_quota, staging_quota = setup_quota_data()
    agreement = origin_quota.agreement
    uri = reverse('schedule:manage-extended-info', kwargs={'slug': agreement.slug})
    _assert_view_propoerties(
        client,
        uri,
        'schedule/manage_extended_information.html',
        'Manage extended information',
        True,
    )


def test_create_agreement_with_no_data(client):
    response = client.post(reverse('schedule:create'), data={})
    assert response.status_code == 200
    expected_errors = {
        'agreement_date_day': ['This field is required.'],
        'agreement_date_month': ['This field is required.'],
        'agreement_date_year': ['This field is required.'],
        'agreement_name': ['This field is required.'],
        'country_codes': ['This field is required.'],
        'slug': ['This field is required.'],
        'version': ['This field is required.'],
    }
    assert response.context['form'].errors == expected_errors


def test_create_agreement(client):
    assert Agreement.objects.count() == 0

    agreement_name = 'An agreement with a very unique name'
    data = {
        'version': '1.0',
        'agreement_name': agreement_name,
        'slug': 'name',
        'country_codes': ['RTD', 'JO'],
        'agreement_date_year': 2000,
        'agreement_date_month': 10,
        'agreement_date_day': 2,

    }
    response = client.post(reverse('schedule:create'), data=data, follow=True)
    assert response.status_code == 200
    assert response.redirect_chain == [(reverse('schedule:manage'), 302)]
    assert agreement_name in str(response.content)

    actual_agreement = Agreement.objects.get(slug=data['slug'])
    assert actual_agreement.country_codes == data['country_codes']
    assert actual_agreement.agreement_date == date(
        data['agreement_date_year'],
        data['agreement_date_month'],
        data['agreement_date_day'],
    )
    assert actual_agreement.agreement_name == data['agreement_name']
    assert actual_agreement.version == data['version']


def test_create_agreement_and_redirect_to_add_extended_information(client):
    assert Agreement.objects.count() == 0

    agreement_name = 'An agreement with a very unique name'
    data = {
        'version': '1.0',
        'agreement_name': agreement_name,
        'slug': 'name',
        'country_codes': ['RTD', 'JO'],
        'agreement_date_year': 2000,
        'agreement_date_month': 10,
        'agreement_date_day': 2,
        'extended_information': True,

    }
    response = client.post(reverse('schedule:create'), data=data, follow=True)
    assert response.status_code == 200
    assert response.redirect_chain == [(reverse('schedule:manage-extended-info', kwargs={'slug': 'name'}), 302)]
    assert 'Manage extended information' in str(response.content)

    actual_agreement = Agreement.objects.get(slug=data['slug'])
    assert actual_agreement.country_codes == data['country_codes']
    assert actual_agreement.agreement_date == date(
        data['agreement_date_year'],
        data['agreement_date_month'],
        data['agreement_date_day'],
    )
    assert actual_agreement.agreement_name == data['agreement_name']
    assert actual_agreement.version == data['version']


def test_manage_extended_information(client):
    agreement = AgreementFactory()
    uri = reverse('schedule:manage-extended-info', kwargs={'slug': agreement.slug})
    data = {
        'origin_quotas': '123\r\n456\r\n890\r\n\r\n',
        'licensed_quotas': '123,1,A\r\n456,2,B\r\n890,1,C\r\n\r\n',
        'scope_quotas': '123,scope1\r\n456,scope2\r\n890,scope3\r\n\r\n',
        'staging_quotas': '123,add1\r\n456,add2\r\n890,add3\r\n\r\n',
    }
    response = client.post(uri, data=data, follow=True)
    assert response.status_code == 200
    assert response.redirect_chain == [(reverse('schedule:manage'), 302)]
    quotas = ExtendedQuota.objects.filter(agreement=agreement)
    assert quotas.count() == 3

    first_quota = quotas.get(quota_order_number_id=123)
    assert first_quota.scope == 'scope1'
    assert first_quota.quota_type == ExtendedQuota.LICENSED
    assert first_quota.addendum == 'add1'
    assert first_quota.is_origin_quota is True
    assert first_quota.opening_balance == 1
    assert first_quota.measurement_unit_code == 'A'

    second_quota = quotas.get(quota_order_number_id=456)
    assert second_quota.scope == 'scope2'
    assert second_quota.quota_type == ExtendedQuota.LICENSED
    assert second_quota.addendum == 'add2'
    assert second_quota.is_origin_quota is True
    assert second_quota.opening_balance == 2
    assert second_quota.measurement_unit_code == 'B'

    third_quota = quotas.get(quota_order_number_id=890)
    assert third_quota.scope == 'scope3'
    assert third_quota.quota_type == ExtendedQuota.LICENSED
    assert third_quota.addendum == 'add3'
    assert third_quota.is_origin_quota is True
    assert third_quota.opening_balance == 1
    assert third_quota.measurement_unit_code == 'C'


def test_manage_extended_information_when_data_is_missing(client):
    agreement = AgreementFactory()
    agreement.save()
    uri = reverse('schedule:manage-extended-info', kwargs={'slug': agreement.slug})
    data = {
        'licensed_quotas': '890,,C\r\n\r\n',
    }
    response = client.post(uri, data=data, follow=True)
    assert response.status_code == 200
    quotas = ExtendedQuota.objects.filter(agreement=agreement)
    third_quota = quotas.get(quota_order_number_id=890)
    assert not third_quota.scope
    assert third_quota.quota_type == ExtendedQuota.LICENSED
    assert not third_quota.addendum
    assert third_quota.is_origin_quota is False
    assert not third_quota.opening_balance
    assert third_quota.measurement_unit_code == 'C'


def test_manage_extended_information_when_data_is_invalid_does_not_save_quota(client):
    agreement = AgreementFactory()
    agreement.save()
    uri = reverse('schedule:manage-extended-info', kwargs={'slug': agreement.slug})
    data = {
        'licensed_quotas': '890,hello,C\r\n\r\n',
    }
    response = client.post(uri, data=data, follow=True)
    assert response.status_code == 200
    quotas = ExtendedQuota.objects.filter(agreement=agreement)
    assert quotas.count() == 0


def test_download_document(client):
    uri = reverse('schedule:download', kwargs={'slug': 'hello'})
    response = client.get(uri)
    assert response.status_code == 302
    assert response.get('Location') == f'/static/tariff/documents/hello_annex.docx'
