from datetime import datetime
from dateutil.relativedelta import relativedelta

from django.contrib.postgres.fields import ArrayField
from django.db import models

from trade_tariff_reference.schedule.constants import BREXIT_VALIDITY_END_DATE, BREXIT_VALIDITY_START_DATE


class Agreement(models.Model):
    slug = models.SlugField(null=True, blank=True, verbose_name='Unique ID')

    country_codes = ArrayField(
        models.CharField(max_length=6),
    )
    gegraphical_area = models.CharField(null=True, blank=True, max_length=200)
    agreement_name = models.CharField(max_length=1024, verbose_name='Agreement title')
    agreement_date = models.DateField()
    version = models.CharField(max_length=20)

    country_name = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.agreement_name} - {self.country_name}'


class QuotaBalance(models.Model):
    agreement = models.ForeignKey('schedule.Agreement', on_delete=models.CASCADE)
    quota_order_number_id = models.CharField(max_length=120)
    method = models.CharField(max_length=120)
    y1_balance = models.CharField(max_length=120, null=True, blank=True)
    yx_balance = models.CharField(max_length=120, null=True, blank=True)
    yx_start = models.DateField(null=True, blank=True)
    measurement_unit_code = models.CharField(max_length=120, null=True, blank=True)
    origin_quota = models.CharField(max_length=120, null=True, blank=True)
    addendum = models.CharField(max_length=255, null=True, blank=True)
    scope = models.CharField(max_length=255, null=True, blank=True)

    @property
    def validity_start_date_2019(self):
        if self.yx_start.month > 3:
            return self.yx_start
        return BREXIT_VALIDITY_START_DATE

    @property
    def validity_end_date_2019(self):
        if self.yx_start.month > 3:
            return self.yx_end
        return BREXIT_VALIDITY_END_DATE

    @property
    def yx_end(self):
        return self.add_year(self.yx_start)

    def add_year(self, date):
        try:
            if type(date) is str:
                date = datetime.strptime(date, "%d/%m/%Y")
            return date + relativedelta(years=1, days=-1)
        except (TypeError, ValueError):
            return
