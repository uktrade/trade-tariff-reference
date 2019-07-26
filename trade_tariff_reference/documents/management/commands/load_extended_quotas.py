from django.core.management.base import BaseCommand

from datetime import datetime

from trade_tariff_reference.schedule.models import ExtendedQuota, Agreement


FILE_NAME = '/app/trade_tariff_reference/documents/fta/config/quota_volume_master.csv'


class Command(BaseCommand):

    help = ''

    def handle(self, *args, **options):
        import csv
        with open(FILE_NAME, 'r') as f:
            data = csv.DictReader(f)
            for row in data:
                agreement = Agreement.objects.get(slug__iexact=row['country'])
                is_origin_quota = True if row['origin_quota'] else False
                quota_type = 'F' if row['method'] == 'FCFS' else 'L'
                start_date = datetime.strptime(row['yx_start'], '%d/%m/%Y').date() if row['yx_start'] else None
                ExtendedQuota.objects.create(
                    agreement=agreement,
                    quota_order_number_id=row['quota_order_number_id'],
                    start_date=start_date,
                    year_start_balance=row['y1_balance'] or None,
                    opening_balance=row['yx_balance'] or None,
                    scope=row['scope'],
                    addendum=row['addendum'],
                    quota_type=quota_type,
                    is_origin_quota=is_origin_quota,
                    measurement_unit_code=row['measurement_unit_code'],
                )
