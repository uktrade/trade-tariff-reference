from datetime import date

import factory


class AgreementFactory(factory.django.DjangoModelFactory):
    country_name = factory.Faker('country')
    agreement_name = factory.Faker('text')
    agreement_date = date(2019, 1, 1)
    table_per_country = 1
    version = '1.0'
    country_codes = factory.List(
        ["IR", "IN"]
    )
    reg_list = factory.List(
        ["I1234567", "I1234568"]
    )
    produce_schedule = True

    class Meta:
        model = 'schedule.Agreement'
