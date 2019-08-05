import random
from datetime import date
from unittest import mock

import factory

from trade_tariff_reference.schedule.models import ExtendedQuota


class AgreementFactory(factory.django.DjangoModelFactory):
    country_name = factory.Faker('country')
    agreement_name = factory.Faker('text')
    agreement_date = date(2019, 1, 1)
    version = '1.0'
    country_codes = factory.List(
        ["IR", "IN"]
    )
    geographical_area = factory.Faker('country')
    slug = factory.Sequence(lambda n: f'country-{n}')
    document = None

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


class DocumentHistoryFactory(factory.django.DjangoModelFactory):
    agreement = factory.SubFactory(AgreementFactory)
    data = {}
    change = {}
    forced = True

    class Meta:
        model = 'schedule.DocumentHistory'


class ExtendedQuotaFactory(factory.django.DjangoModelFactory):
    agreement = factory.SubFactory(AgreementFactory)
    quota_order_number_id = random.randrange(100000, 999999)
    is_origin_quota = True
    measurement_unit_code = 'KGM'
    quota_type = ExtendedQuota.FIRST_COME_FIRST_SERVED
    scope = factory.Faker('text')
    addendum = factory.Faker('text')
    opening_balance = 10000

    class Meta:
        model = 'schedule.ExtendedQuota'


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
