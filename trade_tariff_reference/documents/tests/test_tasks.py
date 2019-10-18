from unittest import mock

import pytest

from trade_tariff_reference.documents.tasks import (
    generate_all_fta_documents,
    generate_fta_document,
    generate_mfn_document,
    generate_mfn_master_document,
    handle_agreement_document_generation_fail,
)
from trade_tariff_reference.schedule.models import DocumentStatus
from trade_tariff_reference.schedule.tests.factories import AgreementFactory


pytestmark = pytest.mark.django_db


@mock.patch('trade_tariff_reference.documents.mfn_master.application.Application.main')
def test_generate_mfn_master_document_task(mock_application_main):
    mock_application_main.return_value = None
    generate_mfn_master_document('HELLO', force=True)
    assert mock_application_main.called is True


@mock.patch('trade_tariff_reference.documents.tasks.generate_mfn_master_document.delay')
@mock.patch('trade_tariff_reference.documents.mfn.application.Application.main')
def test_generate_mfn_document_task(mock_application_main, mock_generate_master_document):
    mock_generate_master_document.return_value = None
    mock_application_main.return_value = None
    generate_mfn_document('HELLO', 1, 2, force=True)
    assert mock_application_main.called is True
    assert mock_generate_master_document.called is True


@mock.patch('trade_tariff_reference.documents.fta.application.Application.main')
def test_generate_fta_document_task(mock_application_main):
    agreement = AgreementFactory()
    mock_application_main.return_value = None
    generate_fta_document(agreement.slug, force=True)
    assert mock_application_main.called is True


@pytest.mark.parametrize(
    'force',
    (
        True, False,
    ),
)
@mock.patch('trade_tariff_reference.documents.tasks.generate_fta_document')
def test_generate_all_fta_documents_task(
    mock_generate_fta_document,
    force,
):
    agreement = AgreementFactory()
    generate_all_fta_documents(background=False, force=force)
    assert mock_generate_fta_document.called is True
    mock_generate_fta_document.assert_called_once_with(agreement.slug, force=force)


@pytest.mark.parametrize(
    'force',
    (
        True, False,
    ),
)
@mock.patch('trade_tariff_reference.documents.tasks.generate_fta_document.delay')
def test_generate_all_fta_documents_task_when_backgrounded(
    mock_delayed_generate_fta_document,
    force,
):
    agreement = AgreementFactory()
    mock_delayed_generate_fta_document.return_value = None
    generate_all_fta_documents(background=True, force=force)
    assert mock_delayed_generate_fta_document.called is True
    mock_delayed_generate_fta_document.assert_called_once_with(agreement.slug, force=force)


def test_handle_agreement_document_generation_fail_with_no_args():
    assert handle_agreement_document_generation_fail(None, None, None, None, None, None) is None


@pytest.mark.parametrize(
    'slug,document_status,expected_status',
    (
        ('hello', DocumentStatus.AVAILABLE, DocumentStatus.AVAILABLE),
        ('agreement-1', DocumentStatus.UNAVAILABLE, DocumentStatus.UNAVAILABLE),
        ('agreement-1', DocumentStatus.GENERATING, DocumentStatus.UNAVAILABLE),
        ('agreement-1', DocumentStatus.AVAILABLE, DocumentStatus.AVAILABLE),
    ),
)
def test_handle_agreement_document_generation_fail_when_agreement_does_not_exist_that_is_generating(
    slug,
    document_status,
    expected_status,
):
    agreement = AgreementFactory(slug='agreement-1', document_status=document_status)
    assert handle_agreement_document_generation_fail(None, None, None, [slug], None, None) is None
    agreement.refresh_from_db()
    assert agreement.document_status == expected_status
