from datetime import datetime

from django.contrib.postgres.fields import ArrayField, JSONField
from django.db import models
from django.shortcuts import reverse

from storages.backends.s3boto3 import S3Boto3Storage

from trade_tariff_reference.documents.functions import format_seasonal_expression, list_to_sql
from trade_tariff_reference.documents.utils import get_document_check_sum
from rest_framework.renderers import JSONRenderer
import json
class DocumentStatus:
    AVAILABLE = 'available'
    UNAVAILABLE = 'unavailable'
    GENERATING = 'generating'

    DOCUMENT_STATUS_CHOICES = (
        (AVAILABLE, 'Available'),
        (UNAVAILABLE, 'Unavailable'),
        (GENERATING, 'Generating'),
    )


class DocumentType:
    SCHEDULE = 'schedule'
    CLASSIFICATION = 'classification'

    DOCUMENT_TYPE_CHOICES = (
        (SCHEDULE, 'Schedule'),
        (CLASSIFICATION, 'Classification'),
    )


class PrivateStorage(S3Boto3Storage):
    default_acl = 'private'


class DocumentStorage(PrivateStorage):
    location = 'documents'


class ChapterNoteStorage(PrivateStorage):
    location = 'documents/mfn/chapter'


class MFNScheduleStorage(PrivateStorage):
    location = 'documents/mfn/schedule'


class MFNClassificationStorage(PrivateStorage):
    location = 'documents/mfn/classification'


class MFNStorage(S3Boto3Storage):
    location = 'documents/mfn/downloads'


class Agreement(models.Model):

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
        choices=DocumentStatus.DOCUMENT_STATUS_CHOICES,
        default=DocumentStatus.UNAVAILABLE,
        max_length=20
    )
    last_checked = models.DateTimeField(null=True, blank=True)

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
        return reverse('schedule:fta:download', kwargs={'slug': self.slug})

    @property
    def edit_url(self):
        return reverse('schedule:fta:edit', kwargs={'slug': self.slug})

    @property
    def regenerate_url(self):
        return reverse('schedule:fta:regenerate', kwargs={'slug': self.slug})

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

    @property
    def is_document_available(self):
        return self.document_status == DocumentStatus.AVAILABLE

    @property
    def is_document_generating(self):
        return self.document_status == DocumentStatus.GENERATING

    @property
    def is_document_unavailable(self):
        return self.document_status == DocumentStatus.UNAVAILABLE

    def to_json(self):
        from trade_tariff_reference.api.serializers import AgreementSerializer
        return json.dumps(AgreementSerializer(instance=self).data)

    def __str__(self):
        return f'{self.agreement_name} - {self.country_name}'


class DocumentHistory(models.Model):
    data = JSONField(null=True, blank=True)
    change = JSONField(null=True, blank=True)
    created_at = models.DateTimeField(db_index=True, null=True, blank=True, auto_now_add=True)
    forced = models.BooleanField()
    remote_file_name = models.CharField(max_length=300, null=True, blank=True)

    class Meta:
        abstract = True
        ordering = ('-created_at',)


class AgreementDocumentHistory(DocumentHistory):
    agreement = models.ForeignKey('schedule.Agreement', on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Agreement Document Histories'

    def __str__(self):
        return f'{self.agreement.slug} - Doc History - {self.created_at}'


class ChapterDocumentHistory(DocumentHistory):
    chapter = models.ForeignKey('schedule.Chapter', on_delete=models.CASCADE)
    document_type = models.CharField(choices=DocumentType.DOCUMENT_TYPE_CHOICES, max_length=100)

    class Meta:
        verbose_name_plural = 'Chapter Document Histories'

    def __str__(self):
        return f'{self.document_type} {self.chapter.chapter_string} - Doc History - {self.created_at}'


class MFNDocumentHistory(DocumentHistory):
    mfn_document = models.ForeignKey('schedule.MFNDocument', on_delete=models.CASCADE)
    document_type = models.CharField(choices=DocumentType.DOCUMENT_TYPE_CHOICES, max_length=100)

    class Meta:
        verbose_name_plural = 'MFN Document Histories'

    def __str__(self):
        return f'{self.document_type} - Doc History - {self.created_at}'


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
    scope = models.CharField(max_length=1000, null=True, blank=True, default='')
    addendum = models.CharField(max_length=1000, null=True, blank=True, default='')
    quota_type = models.CharField(choices=QUOTA_CHOICES, max_length=20)
    is_origin_quota = models.BooleanField(default=False)
    measurement_unit_code = models.CharField(null=True, blank=True, max_length=20, default='')

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

    class Meta:
        unique_together = (('agreement', 'quota_order_number_id'),)


class LatinTerm(models.Model):
    text = models.CharField(max_length=2000)

    def __str__(self):
        return self.text


class SpecialNote(models.Model):
    quota_order_number_id = models.CharField(max_length=120)
    note = models.TextField()

    @property
    def commodity_code(self):
        return self.quota_order_number_id

    def __str__(self):
        return f'{self.quota_order_number_id} - {self.note[0:30]}'


class SeasonalQuota(models.Model):
    quota_order_number_id = models.CharField(max_length=120)

    def __str__(self):
        return f'{self.quota_order_number_id}'


class SeasonalQuotaSeason(models.Model):
    seasonal_quota = models.ForeignKey(SeasonalQuota, on_delete=models.CASCADE, related_name='seasons')
    start_date = models.DateField()
    end_date = models.DateField()
    duty = models.CharField(max_length=1000)

    class Meta:
        ordering = ('start_date',)

    @property
    def formatted_duty(self):
        return format_seasonal_expression(self.duty)

    def __str__(self):
        return f'{self.seasonal_quota.quota_order_number_id} - {self.start_date}/{self.end_date} - {self.duty}'


class Chapter(models.Model):
    id = models.IntegerField(primary_key=True)
    description = models.TextField()
    schedule_document = models.FileField(null=True, blank=True, storage=MFNScheduleStorage())
    schedule_document_created_at = models.DateTimeField(null=True, blank=True)
    schedule_document_status = models.CharField(
        choices=DocumentStatus.DOCUMENT_STATUS_CHOICES,
        default=DocumentStatus.UNAVAILABLE,
        max_length=20
    )
    schedule_last_checked = models.DateTimeField(null=True, blank=True)
    schedule_document_check_sum = models.CharField(max_length=32, null=True, blank=True)
    classification_document = models.FileField(null=True, blank=True, storage=MFNClassificationStorage())
    classification_document_created_at = models.DateTimeField(null=True, blank=True)
    classification_document_status = models.CharField(
        choices=DocumentStatus.DOCUMENT_STATUS_CHOICES,
        default=DocumentStatus.UNAVAILABLE,
        max_length=20
    )
    classification_last_checked = models.DateTimeField(null=True, blank=True)
    classification_document_check_sum = models.CharField(max_length=32, null=True, blank=True)

    @property
    def chapter_string(self):
        return f"{self.id:02d}"

    def get_document_name(self, document_type):
        return f'{document_type}{self.chapter_string}.docx'

    def __str__(self):
        return f'{self.chapter_string} - {self.description}'

    class Meta:
        ordering = ('id',)


class ChapterNote(models.Model):
    chapter = models.OneToOneField(Chapter, on_delete=models.CASCADE, related_name='note')
    document = models.FileField(null=True, blank=True, storage=ChapterNoteStorage())
    document_created_at = models.DateTimeField(null=True, blank=True)
    document_check_sum = models.CharField(max_length=32, null=True, blank=True)

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if self.document:
            self.document_check_sum = get_document_check_sum(self.document.read())

        return super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields
        )

    def __str__(self):
        return f'Chapter Note - {self.chapter.description[0:30]}'

    class Meta:
        ordering = ('chapter__id',)


class MFNDocument(models.Model):
    document = models.FileField(storage=MFNStorage())
    document_created_at = models.DateTimeField()
    last_checked = models.DateTimeField(null=True, blank=True)
    document_check_sum = models.CharField(max_length=32)
    document_type = models.CharField(choices=DocumentType.DOCUMENT_TYPE_CHOICES, max_length=100)
    document_status = models.CharField(
        choices=DocumentStatus.DOCUMENT_STATUS_CHOICES,
        default=DocumentStatus.UNAVAILABLE,
        max_length=20
    )

    @property
    def is_document_available(self):
        return self.document_status == DocumentStatus.AVAILABLE

    @property
    def is_document_generating(self):
        return self.document_status == DocumentStatus.GENERATING

    @property
    def is_document_unavailable(self):
        return self.document_status == DocumentStatus.UNAVAILABLE

    @property
    def download_url(self):
        return reverse('schedule:mfn:download', kwargs={'document_type': self.document_type})

    @property
    def regenerate_url(self):
        return reverse('schedule:mfn:regenerate', kwargs={'document_type': self.document_type})

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['document_type'], name='MFN Document Type constraint'),
        ]

    def to_json(self):
        from trade_tariff_reference.api.serializers import MFNDocumentSerializer
        return json.dumps(MFNDocumentSerializer(instance=self).data)

    def __str__(self):
        return f'Master {self.document_type} MFN document'
