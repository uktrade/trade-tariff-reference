from django.shortcuts import reverse

from freezegun import freeze_time

import pytest

from schedule.tests.factories import AgreementFactory, DocumentHistoryFactory

pytestmark = pytest.mark.django_db


def test_agreement_model():
    agreement = AgreementFactory(
        slug='israel',
        country_name='israel',
        version='2.0',
        country_codes=['IS', '2334'],
        agreement_date='2019-01-01',
        agreement_name='Test agreement',
    )

    agreement.refresh_from_db()
    assert agreement.slug == 'israel'
    assert agreement.country_profile == 'israel'
    assert agreement.geo_ids == "'IS', '2334'"
    assert agreement.country_codes_string == 'IS, 2334'
    assert agreement.agreement_date_short == '01/01/2019'
    assert agreement.agreement_date_long == '1 January 2019'
    assert str(agreement) == f'Test agreement - israel'
    assert agreement.download_url == reverse('schedule:download', kwargs={'slug': agreement.slug})
    assert agreement.edit_url == reverse('schedule:edit', kwargs={'slug': agreement.slug})


@freeze_time('2019-02-01 02:00:00')
def test_document_history_model():
    document_history = DocumentHistoryFactory(agreement__slug='doc-history-slug')
    assert str(document_history) == 'doc-history-slug - Doc History - 2019-02-01 02:00:00+00:00'
