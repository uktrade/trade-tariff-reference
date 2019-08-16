from django.utils.timezone import utc

import factory


class MeasureFactory(factory.django.DjangoModelFactory):
    pass

    class Meta:
        model = 'tariff.Measures'


class MeasureConditionFactory(factory.django.DjangoModelFactory):
    pass

    class Meta:
        model = 'tariff.MeasureConditions'


class MeasureConditionComponentFactory(factory.django.DjangoModelFactory):
    pass

    class Meta:
        model = 'tariff.MeasureConditionComponents'


class MeursingComponentsFactory(factory.django.DjangoModelFactory):
    geographical_area_id = '1011'  # I think UK
    duty_amount = float(2)
    reduction_indicator = 0

    class Meta:
        model = 'tariff.MeursingComponents'


class CurrentMeasureFactory(factory.django.DjangoModelFactory):
    pass

    class Meta:
        model = 'tariff.CurrentMeasures'


class MeasureExcludedGeographicalAreaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'tariff.MeasureExcludedGeographicalAreas'


class GeographicalAreaFactory(factory.django.DjangoModelFactory):
    geographical_area_id = 'IR'
    validity_start_date = factory.Faker('past_datetime', tzinfo=utc)

    class Meta:
        model = 'tariff.GeographicalAreas'


class GoodsNomenclatureFactory(factory.django.DjangoModelFactory):
    producline_suffix = '80'

    class Meta:
        model = 'tariff.GoodsNomenclatures'
