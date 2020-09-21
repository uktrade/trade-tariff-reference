from datetime import datetime, timedelta

from django.db.utils import IntegrityError
from django.shortcuts import reverse

from freezegun import freeze_time

import pytest

from trade_tariff_reference.documents.mfn.constants import CLASSIFICATION, SCHEDULE
from trade_tariff_reference.schedule.tests.factories import (
    AgreementDocumentHistoryFactory,
    AgreementFactory,
    ChapterDocumentHistoryFactory,
    ChapterFactory,
    ChapterNoteFactory,
    ExtendedQuotaFactory,
    LatinTermFactory,
    MFNDocumentFactory,
    MFNDocumentHistoryFactory,
    MFNDocumentWithDocumentFactory,
    MFNTableOfContentFactory,
    SeasonalQuotaFactory,
    SeasonalQuotaSeasonFactory,
    SpecialNoteFactory,
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
    assert str(agreement) == 'Test agreement - israel'
    assert agreement.download_url == reverse('schedule:fta:download', kwargs={'slug': agreement.slug})
    assert agreement.edit_url == reverse('schedule:fta:edit', kwargs={'slug': agreement.slug})
    assert agreement.regenerate_url == reverse('schedule:fta:regenerate', kwargs={'slug': agreement.slug})
    assert agreement.is_document_available is True
    assert agreement.is_document_unavailable is False
    assert agreement.is_document_generating is False


@freeze_time('2019-02-01 02:00:00')
def test_agreement_document_history_model():
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


@freeze_time('2019-02-01 02:00:00')
def test_chapter_document_history_model():
    chapter = ChapterFactory()
    document_history = ChapterDocumentHistoryFactory(chapter=chapter)
    assert str(document_history) == f'schedule {chapter.chapter_string} - Doc History - 2019-02-01 02:00:00+00:00'


@freeze_time('2019-02-01 02:00:00')
def test_mfn_document_history_model():
    mfn_document = MFNDocumentFactory()
    document_history = MFNDocumentHistoryFactory(mfn_document=mfn_document)
    assert str(document_history) == 'schedule - Doc History - 2019-02-01 02:00:00+00:00'


def test_mfn_document_model():
    mfn_document = MFNDocumentWithDocumentFactory(document_type=SCHEDULE)
    mfn_document.refresh_from_db()
    assert str(mfn_document) == 'Master schedule MFN document'
    assert mfn_document.is_document_available is True
    assert mfn_document.is_document_unavailable is False
    assert mfn_document.is_document_generating is False
    assert mfn_document.download_url == reverse('schedule:mfn:download', kwargs={'document_type': SCHEDULE})


def test_mfn_document_model_constraint():
    MFNDocumentWithDocumentFactory(document_type=SCHEDULE)
    with pytest.raises(IntegrityError):
        MFNDocumentWithDocumentFactory(document_type=SCHEDULE)


def test_latin_term_model():
    latin_term = LatinTermFactory(text='lorem')
    assert str(latin_term) == 'lorem'


def test_seasonal_quota_model():
    seasonal_quota = SeasonalQuotaFactory(quota_order_number_id='123456789')
    assert str(seasonal_quota) == '123456789'


@freeze_time('2019-02-01 02:00:00')
def test_seasonal_quota_season_model():
    start_date = datetime.now()
    end_date = start_date + timedelta(days=100)
    seasonal_quota = SeasonalQuotaFactory(quota_order_number_id='123456789')
    seasonal_quota_season = SeasonalQuotaSeasonFactory(
        seasonal_quota=seasonal_quota,
        duty='DUTY DTN',
        start_date=start_date,
        end_date=end_date
    )
    assert str(seasonal_quota_season) == '123456789 - 2019-02-01 02:00:00/2019-05-12 02:00:00 - DUTY DTN'
    assert seasonal_quota_season.formatted_duty == 'DUTY / 100 kg'


def test_chapter_model():
    chapter = ChapterFactory(description='Chapter description')
    assert str(chapter) == '01 - Chapter description'
    assert chapter.chapter_string == '01'
    assert chapter.get_document_name(SCHEDULE) == 'schedule01.docx'


def test_special_note_model():
    special_note = SpecialNoteFactory(
        quota_order_number_id='123456789',
        note='This note will get truncated and we wont be seen'
    )
    assert str(special_note) == '123456789 - This note will get truncated a'
    assert special_note.commodity_code == '123456789'


def test_chapter_note():
    chapter = ChapterFactory(description='Chapter description')
    chapter_note = ChapterNoteFactory(
        chapter=chapter,
    )
    assert str(chapter_note) == 'Chapter Note - Chapter description'
    # MPP TODO: Add a test for document check sum


@pytest.mark.parametrize(
    'document_type,expected_string',
    (
        (
            SCHEDULE, 'Schedule TOC'
        ),
        (
            CLASSIFICATION, 'Classification TOC',
        ),
    ),
)
def test_mfn_table_of_contents(document_type, expected_string):
    mfn_table_contents = MFNTableOfContentFactory(document_type=document_type)
    assert str(mfn_table_contents) == expected_string
