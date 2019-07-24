from datetime import date

import factory


class AgreementFactory(factory.django.DjangoModelFactory):
    country_name = factory.Faker('country')
    agreement_name = factory.Faker('text')
    agreement_date = date(2019, 1, 1)
    version = '1.0'
    country_codes = factory.List(
        ["IR", "IN"]
    )
    gegraphical_area = factory.Faker('country')
    slug = factory.Sequence(lambda n: f'country-{n}')

    class Meta:
        model = 'schedule.Agreement'
