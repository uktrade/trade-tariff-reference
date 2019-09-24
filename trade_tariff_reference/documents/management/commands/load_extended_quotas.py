from datetime import datetime

from django.core.management.base import BaseCommand
from django.db import IntegrityError

from trade_tariff_reference.schedule.models import Agreement, ExtendedQuota


FILE_NAME = '/app/extended.csv'


class Command(BaseCommand):

    help = ''

    def handle(self, *args, **options):
        Agreement.objects.all().delete()
        import csv
        with open(FILE_NAME, 'r') as f:
            data = csv.DictReader(f)
            for num, row in enumerate(data):
                self._run(row)

    def _run(self, row):
        agreement = self.create_agreement(row)
        self.process_origin_quotas(agreement, row)
        self.process_licensed_quotas(agreement, row)
        self.process_scope_quotas(agreement, row)
        self.process_staging_quotas(agreement, row)

    def create_agreement(self, row):
        return Agreement.objects.create(
            slug=row['fta_name'],
            agreement_name=row['agreement_title'],
            version=row['version'],
            country_name=row['geographical_area_name'],
            country_codes=row['country_codes'].split(','),
            agreement_date=datetime.strptime(row['agreement_date'], '%Y-%m-%d').date(),
        )

    def process_origin_quotas(self, agreement, row):
        origin_quotas = row['origin_quotas'].split('\n')
        origin_quotas = list(filter(None, origin_quotas))

        for origin_quota in origin_quotas:
            obj_dict = dict(
                agreement=agreement,
                quota_order_number_id=origin_quota,
                start_date=None,
                year_start_balance=None,
                opening_balance=None,
                scope=None,
                addendum=None,
                quota_type=ExtendedQuota.FIRST_COME_FIRST_SERVED,
                is_origin_quota=True,
                measurement_unit_code=None,
            )
            ExtendedQuota.objects.create(**obj_dict)

    def process_licensed_quotas(self, agreement, row):
        quotas = row['licensed_quota_volumes'].split('\n')
        quotas = list(filter(None, quotas))
        for quota in quotas:
            q, o, unit = quota.split(',')
            obj_dict = dict(
                agreement=agreement,
                quota_order_number_id=q,
                start_date=None,
                year_start_balance=None,
                opening_balance=o,
                scope=None,
                addendum=None,
                quota_type=ExtendedQuota.LICENSED,
                is_origin_quota=False,
                measurement_unit_code=unit,
            )
            ExtendedQuota.objects.create(**obj_dict)

    def strip_staging(self, quota):
        parts = []
        for part in quota.split('"'):
            part = part.rstrip(',')
            part = part.lstrip(',')
            parts.append(part)
        parts = list(filter(None, parts))
        if len(parts) == 1:
            return parts[0].split(',')
        return parts

    def process_staging_quotas(self, agreement, row):
        quotas = row['quota_staging'].split('\n')
        quotas = list(filter(None, quotas))
        for quota in quotas:
            if quota:
                quota = self.strip_staging(quota)
                q, addendum = quota
                try:
                    obj_dict = dict(
                        agreement=agreement,
                        quota_order_number_id=q,
                        start_date=None,
                        year_start_balance=None,
                        opening_balance=None,
                        scope=None,
                        addendum=addendum,
                        quota_type=ExtendedQuota.FIRST_COME_FIRST_SERVED,
                        is_origin_quota=False,
                        measurement_unit_code=None,
                    )
                    ExtendedQuota.objects.create(**obj_dict)
                except IntegrityError:
                    e = ExtendedQuota.objects.get_or_create(
                        agreement=agreement,
                        quota_order_number_id=q,
                    )
                    e.addendum = addendum
                    e.save()

    def process_scope_quotas(self, agreement, row):
        quotas = row['quota_scope'].split('\n')
        quotas = list(filter(None, quotas))
        for quota in quotas:
            if quota:
                q, scope = quota.split(',')
                try:
                    obj_dict = dict(
                        agreement=agreement,
                        quota_order_number_id=q,
                        start_date=None,
                        year_start_balance=None,
                        opening_balance=None,
                        scope=scope,
                        addendum=None,
                        quota_type=ExtendedQuota.FIRST_COME_FIRST_SERVED,
                        is_origin_quota=False,
                        measurement_unit_code=None,
                    )
                    ExtendedQuota.objects.create(**obj_dict)
                except IntegrityError:
                    e = ExtendedQuota.objects.get(
                        agreement=agreement,
                        quota_order_number_id=q,
                    )
                    e.scope = scope
                    e.save()
