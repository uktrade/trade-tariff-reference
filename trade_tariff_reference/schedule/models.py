from datetime import datetime

from django.contrib.postgres.fields import ArrayField, JSONField
from django.db import models
from django.shortcuts import reverse

from trade_tariff_reference.documents.fta.functions import list_to_sql


class Agreement(models.Model):
    slug = models.SlugField(verbose_name='Unique ID', unique=True)

    country_codes = ArrayField(
        models.CharField(max_length=6),
    )
    geographical_area = models.CharField(null=True, blank=True, max_length=200)
    agreement_name = models.CharField(max_length=1024, verbose_name='Agreement title')
    agreement_date = models.DateField()
    version = models.CharField(max_length=20)

    country_name = models.CharField(max_length=200)

    @property
    def country_profile(self):
        return self.slug

    @property
    def geo_ids(self):
        return list_to_sql(self.country_codes)

    @property
    def country_codes_string(self):
        return ', '.join(self.country_codes)

    @property
    def agreement_date_short(self):
        return self.agreement_date.strftime('%d/%m/%Y') if self.agreement_date else ""

    @property
    def agreement_date_long(self):
        return datetime.strftime(self.agreement_date, "%d %B %Y").lstrip("0")if self.agreement_date else ""

    @property
    def download_url(self):
        return reverse('schedule:download', kwargs={'slug': self.slug})

    @property
    def edit_url(self):
        return reverse('schedule:edit', kwargs={'slug': self.slug})

    def __str__(self):
        return f'{self.agreement_name} - {self.country_name}'


class DocumentHistory(models.Model):
    agreement = models.ForeignKey('schedule.Agreement', on_delete=models.CASCADE)
    data = JSONField(null=True, blank=True)
    change = JSONField(null=True, blank=True)
    created_at = models.DateTimeField(db_index=True, null=True, blank=True, auto_now_add=True)
    forced = models.BooleanField()

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.agreement.slug} - Doc History - {self.created_at}'


class ExtendedQuota(models.Model):
    QUOTA_CHOICES = (
        ('F', 'FCFS'),
        ('L', 'Licensed'),
    )
    agreement = models.ForeignKey('schedule.Agreement', on_delete=models.CASCADE)
    quota_order_number_id = models.CharField(max_length=120)
    start_date = models.DateField(null=True, blank=True)
    year_start_balance = models.IntegerField(null=True, blank=True)
    opening_balance = models.IntegerField(null=True, blank=True)
    scope = models.CharField(max_length=1000, null=True, blank=True)
    addendum = models.CharField(max_length=1000, null=True, blank=True)
    quota_type = models.CharField(choices=QUOTA_CHOICES, max_length=20)
    is_origin_quota = models.BooleanField(default=False)
    measurement_unit_code = models.CharField(null=True, blank=True, max_length=20)
