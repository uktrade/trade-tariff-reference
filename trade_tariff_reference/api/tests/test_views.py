from django.shortcuts import reverse

import pytest

from trade_tariff_reference.schedule.models import DocumentStatus
from trade_tariff_reference.schedule.tests.factories import AgreementFactory


pytestmark = pytest.mark.django_db


def sort_list_result(items_list, key='slug'):
    config = {}
    for item in items_list:
        config[item[key]] = item
    return config


class TestAgreementAPIViews:

    def test_empty_agreement_list_view(self, authenticated_client):
        response = authenticated_client.get(reverse('api:agreement-list'))
        assert response.status_code == 200
        assert response.json() == []

    def test_agreement_list_view(self, authenticated_client):
        agreement_1 = AgreementFactory()
        agreement_2 = AgreementFactory()
        response = authenticated_client.get(reverse('api:agreement-list'))
        assert response.status_code == 200
        actual_response = sort_list_result(response.json())
        assert len(actual_response) == 2
        self.assert_agreement(agreement_1, actual_response[agreement_1.slug])
        self.assert_agreement(agreement_2, actual_response[agreement_2.slug])

    @pytest.mark.parametrize(
        'document_status',
        (
            DocumentStatus.AVAILABLE,
            DocumentStatus.GENERATING,
            DocumentStatus.UNAVAILABLE,
        ),
    )
    def test_agreement_detail_view(self, authenticated_client, document_status):
        agreement = AgreementFactory(document_status=document_status)
        response = authenticated_client.get(reverse('api:agreement-detail', kwargs={'slug': agreement.slug}))
        assert response.status_code == 200
        actual_result = response.json()
        self.assert_agreement(agreement, actual_result)

    def assert_agreement(self, agreement, actual_result):
        agreement.refresh_from_db()
        assert set(actual_result.keys()) == {
            'agreement_date',
            'agreement_name',
            'version',
            'country_codes',
            'country_name',
            'document_status',
            'download_url',
            'slug',
            'document_created_at',
            'last_checked',
        }
        assert actual_result['slug'] == agreement.slug
        assert actual_result['agreement_date'] == agreement.agreement_date.strftime('%Y-%m-%d')
        assert actual_result['agreement_name'] == agreement.agreement_name
        assert actual_result['version'] == agreement.version
        assert actual_result['country_name'] == agreement.country_name
        assert actual_result['country_codes'] == agreement.country_codes
        assert actual_result['document_status'] == agreement.document_status
        assert actual_result['document_created_at'] == agreement.document_created_at
        assert actual_result['last_checked'] == agreement.last_checked
        if agreement.document_status == DocumentStatus.AVAILABLE:
            assert actual_result['download_url'].endswith(
                reverse('schedule:fta:download', kwargs={'slug': agreement.slug})
            )
        else:
            assert actual_result['download_url'] == ''
