from django.core.management.base import BaseCommand

from trade_tariff_reference.documents import database


FIRST_QUOTA_BALANCE_OF_THE_YEAR_SQL = """
SELECT quota_order_number_id,
MIN(validity_start_date) as min_start
FROM quota_definitions
WHERE status ='published'
AND (
(validity_start_date >= '2020-01-01' AND validity_start_date <= '2020-12-31')
OR
(validity_end_date >= '2020-01-01' AND validity_end_date <= '2020-12-31')
)
GROUP BY quota_order_number_id
"""


SQL = f"""
SELECT qd.quota_order_number_id,
qd.measurement_unit_code,
qd.initial_volume,
qd.volume,
qd.description,
qd.validity_start_date,
qd.validity_end_date,
qd.quota_definition_sid
FROM ({FIRST_QUOTA_BALANCE_OF_THE_YEAR_SQL}) self JOIN quota_definitions qd
ON qd.quota_order_number_id = self.quota_order_number_id
AND self.min_start = qd.validity_start_date
INNER JOIN quota_order_number_origins qo ON qd.quota_order_number_sid = qo.quota_order_number_sid
AND qo.geographical_area_id = 'CO'
ORDER BY qd.quota_order_number_id
"""


class Command(BaseCommand):

    help = ''

    fields = [
        'quota_order_number_id',
        'validity_start_date',
        'validity_end_date',
        'description'
    ]

    def handle(self, *args, **options):
        db = database.DatabaseConnect()
        result = db.execute_sql(SQL, dict_cursor=True)
        result = list(result)
        for row in result:
            for field in self.fields:
                print(f'{field} - {row[field]}')
            print('----------')

        print(f'Record found: {len(result)}')
