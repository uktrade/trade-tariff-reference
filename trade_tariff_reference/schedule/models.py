from django.db import models
from django.contrib.postgres.fields import ArrayField


class Agreement(models.Model):
    country_name = models.CharField(max_length=200)
    agreement_name = models.CharField(max_length=1024)
    agreement_date = models.DateField()
    table_per_country = models.IntegerField()
    version = models.CharField(max_length=20)
    country_codes = ArrayField(
        models.CharField(max_length=2),
    )
    reg_list = ArrayField(
        models.CharField(max_length=8),
    )
    meursing_reduction = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f'{self.agreement_name} - {self.country_name}'
