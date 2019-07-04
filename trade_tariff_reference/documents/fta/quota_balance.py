from dateutil.relativedelta import relativedelta
from datetime import datetime

BREXIT_VALIDITY_START_DATE = datetime.strptime("29/03/2019", "%d/%m/%Y")
BREXIT_VALIDITY_END_DATE = datetime.strptime("31/12/2019", "%d/%m/%Y")


class QuotaBalance:

    def __init__(
        self, quota_order_number_id, country, method, y1_balance, yx_balance, yx_start, measurement_unit_code,
        origin_quota, addendum, scope
    ):
        self.quota_order_number_id = quota_order_number_id
        self.country = country
        self.method = method
        self.y1_balance = y1_balance
        self.yx_balance = yx_balance
        self.yx_start = yx_start
        self.yx_end = self.add_year(self.yx_start)
        self.measurement_unit_code = measurement_unit_code.strip()
        self.addendum = addendum.strip()
        self.scope = scope.strip()

        if origin_quota == "Y":
            origin_quota = "Yes"
        self.origin_quota = origin_quota

        self.validity_start_date_2019 = BREXIT_VALIDITY_START_DATE
        self.validity_end_date_2019 = BREXIT_VALIDITY_END_DATE
        self.get_year_one_dates()

    def add_year(self, date):
        try:
            if type(date) is str:
                date = datetime.strptime(date, "%d/%m/%Y")
            return date + relativedelta(years=1, days=-1)
        except (TypeError, ValueError):
            print("An error has occurred: cannot work out date / time of quota", self.quota_order_number_id)
            return

    def get_year_one_dates(self):
        start_date = datetime.strptime(self.yx_start, "%d/%m/%Y")
        if start_date.month > 3:
            self.validity_start_date_2019 = start_date
            self.validity_end_date_2019 = self.add_year(start_date)
