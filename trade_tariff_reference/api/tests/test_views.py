from datetime import datetime

from django.shortcuts import reverse

import pytest

from trade_tariff_reference.documents.mfn.constants import CLASSIFICATION, SCHEDULE
from trade_tariff_reference.schedule.models import DocumentStatus
from trade_tariff_reference.schedule.tests.factories import AgreementFactory, MFNDocumentFactory


pytestmark = pytest.mark.django_db


def sort_list_result(items_list, key='slug'):
    config = {}
    for item in items_list:
        config[item[key]] = item
    return config


class TestAgreementAPIViews:

    def test_empty_list_view(self, authenticated_client):
        response = authenticated_client.get(reverse('api:agreement-list'))
        assert response.status_code == 200
        assert response.json() == []

    def test_list_view(self, authenticated_client):
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
    def test_detail_view(self, authenticated_client, document_status):
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


class TestMFNDocumentAPIViews:

    def test_empty_list_view(self, authenticated_client):
        response = authenticated_client.get(reverse('api:mfn-document-list'))
        assert response.status_code == 200
        assert response.json() == []

    def test_list_view(self, authenticated_client):
        classification_mfn_document = MFNDocumentFactory(document_type=CLASSIFICATION)
        schedule_mfn_document = MFNDocumentFactory(document_type=SCHEDULE, document_status=DocumentStatus.UNAVAILABLE)
        response = authenticated_client.get(reverse('api:mfn-document-list'))
        assert response.status_code == 200
        actual_response = sort_list_result(response.json(), key='document_type')
        assert len(actual_response) == 2
        self.assert_mfn_document(classification_mfn_document, actual_response[CLASSIFICATION])
        self.assert_mfn_document(schedule_mfn_document, actual_response[SCHEDULE])

    @pytest.mark.parametrize(
        'document_status',
        (
            DocumentStatus.AVAILABLE,
            DocumentStatus.GENERATING,
            DocumentStatus.UNAVAILABLE,
        ),
    )
    def test_detail_view(self, authenticated_client, document_status):
        schedule_mfn_document = MFNDocumentFactory(document_type=SCHEDULE)
        response = authenticated_client.get(reverse('api:mfn-document-detail', kwargs={'document_type': SCHEDULE}))
        assert response.status_code == 200
        actual_response = response.json()
        self.assert_mfn_document(schedule_mfn_document, actual_response)

    def assert_mfn_document(self, mfn_document, actual_result):
        mfn_document.refresh_from_db()
        assert set(actual_result.keys()) == {
            'document_type',
            'download_url',
            'document_status',
            'document_created_at',
            'last_checked'
        }
        assert actual_result['document_status'] == mfn_document.document_status
        assert actual_result['document_type'] == mfn_document.document_type
        self.assert_date(actual_result['document_created_at'], mfn_document.document_created_at)
        self.assert_date(actual_result['last_checked'], mfn_document.last_checked)
        if mfn_document.document_status == DocumentStatus.AVAILABLE:
            assert actual_result['download_url'].endswith(
                reverse('schedule:mfn:download', kwargs={'document_type': mfn_document.document_type})
            )
        else:
            assert actual_result['download_url'] == ''

    def assert_date(self, actual_date, expected_date):
        if actual_date:
            actual_date = datetime.strptime(actual_date, "%Y-%m-%dT%H:%M:%S.%f%z")
        assert actual_date == expected_date
