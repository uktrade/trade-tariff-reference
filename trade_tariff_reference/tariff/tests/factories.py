import factory


class MeasureFactory(factory.django.DjangoModelFactory):
    pass

    class Meta:
        model = 'tariff.Measures'
