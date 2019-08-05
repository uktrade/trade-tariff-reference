from datetime import datetime

BREXIT_VALIDITY_START_DATE = datetime.strptime("29/03/2019", "%d/%m/%Y")
BREXIT_VALIDITY_END_DATE = datetime.strptime("31/12/2019", "%d/%m/%Y")


ORIGIN_QUOTA_FIELDS = ['quota_order_number_id']
LICENSED_QUOTA_FIELDS = ['quota_order_number_id', 'opening_balance', 'measurement_unit_code']
SCOPE_QUOTA_FIELDS = ['quota_order_number_id', 'scope']
STAGING_QUOTA_FIELDS = ['quota_order_number_id', 'addendum']

DOCX_CONTENT_TYPE = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
