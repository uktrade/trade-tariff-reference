import random
from datetime import date

from django.utils.timezone import utc

import factory

from trade_tariff_reference.documents.fta.constants import PUBLISHED


class MeasureFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'tariff.Measures'


class MeasureConditionFactory(factory.django.DjangoModelFactory):
    status = PUBLISHED

    class Meta:
        model = 'tariff.MeasureConditions'


class MeasureConditionComponentFactory(factory.django.DjangoModelFactory):
    status = PUBLISHED

    class Meta:
        model = 'tariff.MeasureConditionComponents'


class MeursingComponentsFactory(factory.django.DjangoModelFactory):
    geographical_area_id = '1011'  # I think UK
    duty_amount = float(2)
    reduction_indicator = 0

    class Meta:
        model = 'tariff.MeursingComponents'


class CurrentMeasureFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'tariff.CurrentMeasures'


class MeasureExcludedGeographicalAreaFactory(factory.django.DjangoModelFactory):
    status = PUBLISHED

    class Meta:
        model = 'tariff.MeasureExcludedGeographicalAreas'


class GeographicalAreaFactory(factory.django.DjangoModelFactory):
    geographical_area_id = 'IR'
    validity_start_date = factory.Faker('past_datetime', tzinfo=utc)
    status = PUBLISHED

    class Meta:
        model = 'tariff.GeographicalAreas'


class GoodsNomenclatureFactory(factory.django.DjangoModelFactory):
    producline_suffix = '80'
    status = PUBLISHED

    class Meta:
        model = 'tariff.GoodsNomenclatures'


class ChapterSectionFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'tariff.ChaptersSections'


class QuotaOrderNumberFactory(factory.django.DjangoModelFactory):
    status = PUBLISHED
    validity_start_date = date(2020, 1, 1)
    validity_end_date = date(2020, 12, 31)
    id = factory.LazyAttribute(lambda q: str(random.randrange(100000, 999999)))
    quota_order_number_sid = factory.LazyAttribute(
        lambda q: str(q.id)
    )

    class Meta:
        model = 'tariff.QuotaOrderNumbers'


class QuotaDefinitionFactory(factory.django.DjangoModelFactory):
    status = PUBLISHED
    quota_order_number_sid = factory.LazyAttribute(
        lambda q: str(q.quota_order_number.quota_order_number_sid)
    )
    validity_start_date = date(2020, 1, 1)
    validity_end_date = date(2020, 12, 31)
    quota_order_number = factory.SubFactory(
        QuotaOrderNumberFactory,
        quota_order_number_sid=factory.SelfAttribute('..quota_order_number_sid')
    )

    class Meta:
        model = 'tariff.QuotaDefinitions'


class QuotaOrderNumberOriginFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'tariff.QuotaOrderNumberOrigins'
