from django.shortcuts import reverse

from freezegun import freeze_time

import pytest

from schedule.tests.factories import AgreementFactory, DocumentHistoryFactory, ExtendedQuotaFactory

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
    assert quota.scope_quota_string == '10000,my-scope'
    assert quota.staging_quota_string == '10000,my-addendum'


def test_agreemeent_quotas():
    agreement = AgreementFactory()
    origin_quota = ExtendedQuotaFactory(
        agreement=agreement,
        is_origin_quota=True,
        quota_order_number_id=10,
        scope='',
        addendum='',
    )
    licensed_quota = ExtendedQuotaFactory(
        agreement=agreement,
        is_origin_quota=False,
        quota_order_number_id=11,
        quota_type='L',
        opening_balance=1000,
        scope='',
        addendum='',
    )
    scope_quota = ExtendedQuotaFactory(
        agreement=agreement,
        is_origin_quota=False,
        quota_order_number_id=12,
        scope='scope',
        addendum='',
    )
    staging_quota = ExtendedQuotaFactory(
        agreement=agreement,
        is_origin_quota=False,
        scope='',
        addendum='addendum',
        quota_order_number_id=13
    )
    assert list(agreement.origin_quotas.values_list('pk', flat=True)) == [origin_quota.pk]
    assert list(agreement.licensed_quotas.values_list('pk', flat=True)) == [licensed_quota.pk]
    assert list(agreement.scope_quotas.values_list('pk', flat=True)) == [scope_quota.pk]
    assert list(agreement.staging_quotas.values_list('pk', flat=True)) == [staging_quota.pk]
