from unittest import mock


import pytest

from rest_framework.test import APIClient
from django.shortcuts import reverse

from trade_tariff_reference.schedule.tests.factories import AgreementFactory


pytestmark = pytest.mark.django_db


@mock.patch('authbroker_client.utils.get_profile')
@mock.patch('authbroker_client.utils.get_client')
def authenticated_client_with_login(mock_get_profile, mock_get_client,  user):
    mock_get_client.return_value = mock.MagicMock(authorized=True)
    mock_get_profile.return_value = {'email': user.email, 'first_name': user.first_name, 'last_name': user.last_name}
    client = APIClient()
    client.login()
    return client


def authenticated_client(user):
    client = APIClient()
    return client


def sort_list_result(items_list, key='slug'):
    config = {}
    for item in items_list:
        config[item[key]] = item
    return config


class TestAgreementAPIViews:

    def test_empty_agreement_list_view(self, user):
        client = authenticated_client(user)
        response = client.get(reverse('api:agreement-list'), user=user)
        assert response.status_code == 200
        assert response.json() == []

    def test_agreement_list_view(self, user):
        client = authenticated_client(user)
        agreement_1 = AgreementFactory()
        agreement_2 = AgreementFactory()
        response = client.get(reverse('api:agreement-list'), user=user)
        assert response.status_code == 200
        actual_response = sort_list_result(response.json())
        assert len(actual_response) == 2
        self.assert_agreement(agreement_1, actual_response[agreement_1.slug])
        self.assert_agreement(agreement_2, actual_response[agreement_2.slug])

    def test_agreement_detail_view(self, user):
        client = authenticated_client(user)
        agreement = AgreementFactory()
        response = client.get(reverse('api:agreement-detail', kwargs={'slug': agreement.slug}), user=user)
        assert response.status_code == 200
        actual_result = response.json()
        self.assert_agreement(agreement, actual_result)

    def assert_agreement(self, agreement, actual_result):
        assert set(actual_result.keys()) == {
            'agreement_date',
            'agreement_name',
            'version',
            'country_codes',
            'country_name',
            'document_status',
            'download_url',
            'slug',
            'document_created_at'
        }
        assert actual_result['slug'] == agreement.slug
        assert actual_result['agreement_date'] == agreement.agreement_date.strftime('%Y-%m-%d')
        assert actual_result['agreement_name'] == agreement.agreement_name
        assert actual_result['version'] == agreement.version
        assert actual_result['country_name'] == agreement.country_name
        assert actual_result['country_codes'] == agreement.country_codes
        assert actual_result['document_status'] == agreement.document_status
        assert actual_result['document_created_at'] == agreement.document_created_at
        assert actual_result['download_url'].endswith(reverse('schedule:download', kwargs={'slug': agreement.slug}))



