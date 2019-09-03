import random
from datetime import date, datetime
from unittest import mock

import factory

from trade_tariff_reference.documents.mfn.constants import SCHEDULE
from trade_tariff_reference.schedule.models import DocumentStatus, ExtendedQuota
from trade_tariff_reference.tariff.tests.factories import GeographicalAreaFactory


class AgreementFactory(factory.django.DjangoModelFactory):
    country_name = factory.Faker('country')
    agreement_name = factory.Faker('text')
    agreement_date = date(2019, 1, 1)
    version = '1.0'
    country_codes = factory.List(
        [
            factory.LazyAttribute(lambda o: GeographicalAreaFactory(geographical_area_id='IR').geographical_area_id),
            factory.LazyAttribute(lambda o: GeographicalAreaFactory(geographical_area_id='IN').geographical_area_id),
        ]
    )
    slug = factory.Sequence(lambda n: f'country-{n}')
    document = None
    document_status = DocumentStatus.AVAILABLE

    class Meta:
        model = 'schedule.Agreement'

    @classmethod
    def create(cls, *args, **kwargs):
        """ Workaround for FileField being a post generation attribute """
        with mock.patch('storages.backends.s3boto3.S3Boto3Storage.save') as mock_file_save:
            mock_file_save.return_value = 'annex.docx'
            return super().create(*args, **kwargs)


class AgreementWithDocumentFactory(AgreementFactory):
    document = factory.django.FileField(filename='annex.docx')


class AgreementDocumentHistoryFactory(factory.django.DjangoModelFactory):
    agreement = factory.SubFactory(AgreementFactory)
    data = {}
    change = {}
    forced = True

    class Meta:
        model = 'schedule.AgreementDocumentHistory'


class ExtendedQuotaFactory(factory.django.DjangoModelFactory):
    agreement = factory.SubFactory(AgreementFactory)
    quota_order_number_id = str(random.randrange(100000, 999999))
    is_origin_quota = True
    measurement_unit_code = 'KGM'
    quota_type = ExtendedQuota.FIRST_COME_FIRST_SERVED
    scope = factory.Faker('text')
    addendum = factory.Faker('text')
    opening_balance = 10000

    class Meta:
        model = 'schedule.ExtendedQuota'


class LatinTermFactory(factory.django.DjangoModelFactory):
    text = factory.Faker('text')

    class Meta:
        model = 'schedule.LatinTerm'


class SpecialNoteFactory(factory.django.DjangoModelFactory):
    quota_order_number_id = str(random.randrange(100000, 999999))
    note = factory.Faker('text')

    class Meta:
        model = 'schedule.SpecialNote'


class ChapterFactory(factory.django.DjangoModelFactory):
    id = 1
    description = factory.Faker('text')

    class Meta:
        model = 'schedule.Chapter'
        django_get_or_create = ('id',)


class ChapterWithDocumentFactory(ChapterFactory):
    schedule_document = factory.django.FileField(filename='schedule_chapter.docx')
    classification_document = factory.django.FileField(filename='classification_chapter.docx')

    @classmethod
    def create(cls, *args, **kwargs):
        """ Workaround for FileField being a post generation attribute """
        with mock.patch('storages.backends.s3boto3.S3Boto3Storage.save') as mock_file_save:
            mock_file_save.return_value = 'annex.docx'
            return super().create(*args, **kwargs)


class ChapterNoteFactory(factory.django.DjangoModelFactory):
    chapter = factory.SubFactory(ChapterFactory)
    document = None
    document_created_at = None
    document_check_sum = None

    class Meta:
        model = 'schedule.ChapterNote'


class ChapterNoteWithDocumentFactory(factory.django.DjangoModelFactory):
    document = factory.django.FileField(filename='chapter_note.docx')


class ChapterDocumentHistoryFactory(factory.django.DjangoModelFactory):
    chapter = factory.SubFactory(ChapterFactory)
    document_type = SCHEDULE
    data = {}
    change = {}
    forced = True

    class Meta:
        model = 'schedule.ChapterDocumentHistory'


class MFNDocumentFactory(factory.django.DjangoModelFactory):
    document_type = SCHEDULE
    document = None
    document_status = DocumentStatus.AVAILABLE
    document_created_at = datetime.now()
    document_check_sum = ''

    class Meta:
        model = 'schedule.MFNDocument'

    @classmethod
    def create(cls, *args, **kwargs):
        """ Workaround for FileField being a post generation attribute """
        with mock.patch('storages.backends.s3boto3.S3Boto3Storage.save') as mock_file_save:
            mock_file_save.return_value = 'annex.docx'
            return super().create(*args, **kwargs)


class MFNDocumentWithDocumentFactory(MFNDocumentFactory):
    document = factory.django.FileField(filename='mfn.docx')
    document_check_sum = '5d41402abc4b2a76b9719d911017c592'


class MFNDocumentHistoryFactory(factory.django.DjangoModelFactory):
    mfn_document = factory.SubFactory(MFNDocumentFactory)
    document_type = SCHEDULE
    data = {}
    change = {}
    forced = True

    class Meta:
        model = 'schedule.MFNDocumentHistory'


class SeasonalQuotaFactory(factory.django.DjangoModelFactory):
    quota_order_number_id = str(random.randrange(100000, 999999))

    class Meta:
        model = 'schedule.SeasonalQuota'


class SeasonalQuotaSeasonFactory(factory.django.DjangoModelFactory):
    seasonal_quota = factory.SubFactory(SeasonalQuotaFactory)
    start_date = factory.Faker('date')
    end_date = factory.Faker('date')

    class Meta:
        model = 'schedule.SeasonalQuotaSeason'


def setup_quota_data():
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
        addendum='"addendum"',
        quota_order_number_id=13
    )
    return origin_quota, licensed_quota, scope_quota, staging_quota
