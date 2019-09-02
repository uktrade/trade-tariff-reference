from django.shortcuts import reverse

from freezegun import freeze_time

import pytest

from schedule.tests.factories import (
    AgreementDocumentHistoryFactory,
    AgreementFactory,
    ExtendedQuotaFactory,
    setup_quota_data,
)

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
    assert agreement.download_url == reverse('schedule:fta:download', kwargs={'slug': agreement.slug})
    assert agreement.edit_url == reverse('schedule:fta:edit', kwargs={'slug': agreement.slug})
    assert agreement.is_document_available is True
    assert agreement.is_document_unavailable is False
    assert agreement.is_document_generating is False


@freeze_time('2019-02-01 02:00:00')
def test_document_history_model():
    document_history = AgreementDocumentHistoryFactory(agreement__slug='doc-history-slug')
    assert str(document_history) == 'doc-history-slug - Doc History - 2019-02-01 02:00:00+00:00'


def test_extended_quota_model():
    quota = ExtendedQuotaFactory(
        quota_order_number_id=10000,
        quota_type='F',
        is_origin_quota=True,
        opening_balance=123456,
        measurement_unit_code='KG',
        scope='my-scope',
        addendum='my-addendum',
    )
    assert str(quota) == f'10000 - F - {quota.agreement}'
    assert quota.origin_quota_string == '10000'
    assert quota.licensed_quota_string == '10000,123456,KG'
    assert quota.scope_quota_string == '10000,"my-scope"'
    assert quota.staging_quota_string == '10000,"my-addendum"'


def test_agreemeent_quotas():
    origin_quota, licensed_quota, scope_quota, staging_quota = setup_quota_data()
    agreement = origin_quota.agreement
    assert list(agreement.origin_quotas.values_list('pk', flat=True)) == [origin_quota.pk]
    assert list(agreement.licensed_quotas.values_list('pk', flat=True)) == [licensed_quota.pk]
    assert list(agreement.scope_quotas.values_list('pk', flat=True)) == [scope_quota.pk]
    assert list(agreement.staging_quotas.values_list('pk', flat=True)) == [staging_quota.pk]
