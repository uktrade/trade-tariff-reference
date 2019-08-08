from datetime import datetime

from django.contrib.postgres.fields import ArrayField, JSONField
from django.db import models
from django.shortcuts import reverse

from storages.backends.s3boto3 import S3Boto3Storage

from trade_tariff_reference.documents.fta.functions import list_to_sql


class DocumentStorage(S3Boto3Storage):
    location = 'documents'
    default_acl = 'private'


class Agreement(models.Model):
    AVAILABLE = 'available'
    UNAVAILABLE = 'unavailable'
    GENERATING = 'generating'

    DOCUMENT_STATUS_CHOICES = (
        (AVAILABLE, 'Available'),
        (UNAVAILABLE, 'Unavailable'),
        (GENERATING, 'Generating'),
    )

    slug = models.SlugField(verbose_name='Unique ID', unique=True)

    country_codes = ArrayField(
        models.CharField(max_length=6),
    )
    agreement_name = models.CharField(max_length=1024, verbose_name='Agreement title')
    agreement_date = models.DateField()
    version = models.CharField(max_length=20)

    country_name = models.CharField(max_length=200)
    document = models.FileField(null=True, blank=True, storage=DocumentStorage())
    document_created_at = models.DateTimeField(null=True, blank=True)
    document_status = models.CharField(
        choices=DOCUMENT_STATUS_CHOICES, default=UNAVAILABLE, max_length=20
    )

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

    @property
    def origin_quotas(self):
        return self.quotas.filter(is_origin_quota=True)

    @property
    def licensed_quotas(self):
        return self.quotas.filter(quota_type='L')

    @property
    def scope_quotas(self):
        return self.quotas.filter(scope__isnull=False).exclude(scope='')

    @property
    def staging_quotas(self):
        return self.quotas.filter(addendum__isnull=False).exclude(addendum='')

    def __str__(self):
        return f'{self.agreement_name} - {self.country_name}'


class DocumentHistory(models.Model):
    agreement = models.ForeignKey('schedule.Agreement', on_delete=models.CASCADE)
    data = JSONField(null=True, blank=True)
    change = JSONField(null=True, blank=True)
    created_at = models.DateTimeField(db_index=True, null=True, blank=True, auto_now_add=True)
    forced = models.BooleanField()
    remote_file_name = models.CharField(max_length=300, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Document Histories'
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.agreement.slug} - Doc History - {self.created_at}'


class ExtendedQuota(models.Model):
    LICENSED = 'L'
    FIRST_COME_FIRST_SERVED = 'F'

    QUOTA_CHOICES = (
        (FIRST_COME_FIRST_SERVED, 'FCFS'),
        (LICENSED, 'Licensed'),
    )
    agreement = models.ForeignKey('schedule.Agreement', on_delete=models.CASCADE, related_name='quotas')
    quota_order_number_id = models.CharField(max_length=120)
    start_date = models.DateField(null=True, blank=True)
    year_start_balance = models.IntegerField(null=True, blank=True)
    opening_balance = models.IntegerField(null=True, blank=True)
    scope = models.CharField(max_length=1000, null=True, blank=True)
    addendum = models.CharField(max_length=1000, null=True, blank=True)
    quota_type = models.CharField(choices=QUOTA_CHOICES, max_length=20)
    is_origin_quota = models.BooleanField(default=False)
    measurement_unit_code = models.CharField(null=True, blank=True, max_length=20)

    @property
    def origin_quota_string(self):
        return f'{self.quota_order_number_id}'

    @property
    def licensed_quota_string(self):
        return f'{self.quota_order_number_id},{self.opening_balance},{self.measurement_unit_code}'

    @property
    def scope_quota_string(self):
        scope = self.scope.replace('"', '') if self.scope else ''
        if scope:
            scope = f'"{scope}"'
        return f'{self.quota_order_number_id},{scope}'

    @property
    def staging_quota_string(self):
        addendum = self.addendum.replace('"', '') if self.addendum else ''
        if addendum:
            addendum = f'"{addendum}"'
        return f'{self.quota_order_number_id},{addendum}'

    def __str__(self):
        return f'{self.quota_order_number_id} - {self.quota_type} - {self.agreement}'
