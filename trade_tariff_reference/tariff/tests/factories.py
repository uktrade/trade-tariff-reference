import random

import factory


def get_random_id():
    # Temporary hack to allow reuse-db to be used.
    return random.randint(0, 1000)


class MeasureFactory(factory.django.DjangoModelFactory):
    pass

    class Meta:
        model = 'tariff.Measures'


class MeursingComponentsFactory(factory.django.DjangoModelFactory):
    measure_sid = factory.LazyFunction(get_random_id)
    geographical_area_id = '1011'  # I think UK
    duty_amount = float(2)

    class Meta:
        model = 'tariff.MeursingComponents'
