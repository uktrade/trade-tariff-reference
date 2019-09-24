from datetime import datetime

from dateutil.relativedelta import relativedelta

from django.conf import settings


class QuotaBalance:

    def __init__(
        self, quota_order_number_id, country, method, y1_balance, yx_balance, yx_start, measurement_unit_code,
        origin_quota, addendum, scope
    ):
        self.quota_order_number_id = quota_order_number_id
        self.country = country
        self.method = method
        self.y1_balance = y1_balance or 0
        self.yx_balance = yx_balance or 0
        self.yx_start = self.format_date(yx_start)
        self.yx_end = self.add_year(self.yx_start)
        self.measurement_unit_code = measurement_unit_code or ""
        self.addendum = addendum or ""
        self.scope = scope or ""

        if origin_quota == "Y":
            origin_quota = "Yes"
        self.origin_quota = origin_quota

        self.validity_start_date_2019 = settings.BREXIT_VALIDITY_START_DATE
        self.validity_end_date_2019 = settings.BREXIT_VALIDITY_END_DATE
        self.get_year_one_dates()

    def add_year(self, date):
        if not date:
            return
        try:
            return date + relativedelta(years=1, days=-1)
        except (TypeError, ValueError):
            return

    def get_year_one_dates(self):
        if not self.yx_start:
            return
        if self.yx_start.month > 3:
            self.validity_start_date_2019 = self.yx_start
            self.validity_end_date_2019 = self.add_year(self.yx_start)

    def format_date(self, date_string):
        if date_string and isinstance(date_string, str):
            try:
                return datetime.strptime(date_string, "%d/%m/%Y")
            except (TypeError, ValueError):
                return
