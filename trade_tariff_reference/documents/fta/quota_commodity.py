import trade_tariff_reference.documents.functions as functions
from trade_tariff_reference.documents.fta.commodity import BaseCommodity, format_commodity_code
from trade_tariff_reference.documents.fta.constants import NUMBER_OF_DAYS_PER_YEAR
from trade_tariff_reference.documents.fta.measure import Period


class QuotaCommodity(BaseCommodity):

    def __init__(self, commodity_code, quota_order_number_id):
        self.commodity_code = functions.mstr(commodity_code)
        self.commodity_code_formatted = format_commodity_code(self.commodity_code)
        self.quota_order_number_id = functions.mstr(quota_order_number_id)
        self.measure_list = []
        self.duty_string = ""
        self.suppress = False

    def is_entry_price(self):
        return any("Entry Price" in measure.combined_duty for measure in self.measure_list)

    def is_seasonal(self, contains_siv, is_all_full_year, is_infinite):
        return not any([contains_siv, is_all_full_year, is_infinite])

    def check_for_restarted_measures(self):
        # Check for EU screw-ups where they restarted a Measure for no reason
        # List all of the measures, remove the measures that are 365 days long
        # Then add the other ones up: if they add up to 365, then treat this as a whole year Measure

        day_count = 0
        for measure in self.measure_list:
            if measure.extent != NUMBER_OF_DAYS_PER_YEAR:
                day_count += measure.extent

        # Check to see if this is a full year Measure
        if day_count == NUMBER_OF_DAYS_PER_YEAR:
            return True
        return False

    def suppress_if_eps_or_full_year(self, is_all_full_year, contains_siv):
        if is_all_full_year or contains_siv:
            for measure in self.measure_list[:-1]:
                measure.suppress = True

    def process_seasonal_measure(self, contains_siv, is_all_full_year, is_infinite):
        full_period_list = []
        for measure in self.measure_list:
            if not contains_siv and not is_all_full_year and not is_infinite:
                obj_period = str(measure.validity_start_day) + "/" + str(measure.validity_start_month)
                full_period_list.append(obj_period)

        if len(full_period_list) > 0:
            partial = set(full_period_list)
        else:
            partial = []

        partial_period_list = []

        if len(partial) > 0:
            for obj in partial:
                obj_split = obj.split("/")
                obj_period = Period(int(obj_split[0]), int(obj_split[1]))
                partial_period_list.append(obj_period)
        return partial_period_list

    def resolve_measures(self):
        contains_siv = self.is_entry_price()
        is_infinite = self.is_any_infinite()
        is_all_full_year = self.is_all_full_year()

        if self.check_for_restarted_measures():
            is_all_full_year = True

        # If it is, then only show the chronologically last Duty, as any others will be from a previous year
        # Also check to see if this is on the entry price system. If this is EPS, then it is not going to
        # be seasonal as well - they appear to be mutually exclusive
        self.suppress_if_eps_or_full_year(is_all_full_year, contains_siv)

        # So if the Measure is neither infinite, nor entry price, nor is it a full year Measure
        # Then it must be seasonal
        partial_period_list = self.process_seasonal_measure(contains_siv, is_all_full_year, is_infinite)

        is_seasonal = self.is_seasonal(contains_siv, is_all_full_year, is_infinite)
        if is_seasonal:
            self.mark_measure(partial_period_list)

        self.duty_string = self.get_duty_string(is_seasonal)

    def get_duty_string(self, is_seasonal):
        duty_string = ""
        for measure in self.measure_list:
            if not measure.suppress:
                if is_seasonal:
                    duty_string = measure.combined_duty
                else:
                    duty_string += measure.combined_duty
        return duty_string
