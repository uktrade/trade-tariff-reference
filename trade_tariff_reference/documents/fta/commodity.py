import logging

from django.conf import settings

import trade_tariff_reference.documents.fta.functions as functions
from trade_tariff_reference.documents.fta.constants import INFINITE_MEASURE_EXTENT
from trade_tariff_reference.documents.fta.measure import Period


logger = logging.getLogger(__name__)


def format_commodity_code(commodity_code):
    end_values = commodity_code[8:10]
    if end_values == '00':
        end_values = ''

    formatted_string = (
        f'{commodity_code[0:4]} {commodity_code[4:6]}'
        f' {commodity_code[6:8]} {end_values}'
    )
    formatted_string = formatted_string.strip()
    return formatted_string


class BaseCommodity:
    measure_list = []

    def is_any_infinite(self):
        return any(measure.extent == INFINITE_MEASURE_EXTENT for measure in self.measure_list)

    def is_all_full_year(self):
        # Check if the measure is exactly a year long; in which case only a single measure
        # can be shown - it cannot be seasonal

        full_years = [365, 366, 730, 731, 1095, 1096, 1460, 1461, 1825, 1826, 2190, 2191]
        return all(measure.extent in full_years for measure in self.measure_list)

    def mark_measure(self, partial_period_list):
        reversed_list = self.measure_list
        reversed_list.reverse()

        for measure in reversed_list:
            for obj in partial_period_list:
                if not obj.marked:
                    if (
                        int(measure.validity_start_day) == int(obj.validity_start_day)
                        and int(measure.validity_start_month) == int(obj.validity_start_month)
                    ):
                        measure.marked = True
                        obj.marked = True

        for measure in reversed_list:
            if not measure.marked:
                measure.suppress = True


class Commodity(BaseCommodity):

    def __init__(self, commodity_code):
        self.commodity_code = functions.mstr(commodity_code)
        self.commodity_code_formatted = format_commodity_code(self.commodity_code)
        self.measure_list = []
        self.duty_string = ""
        self.suppress = False
        self.date_brexit = settings.BREXIT_VALIDITY_END_DATE

    def resolve_measures(self):
        is_infinite = self.is_any_infinite()
        is_all_full_year = self.is_all_full_year()

        # If the measure is a full year measure, then we should only show one measure
        # under all circumstances; therefore remove all but the 1st item in the list
        # The 1st item is the most recent
        if is_all_full_year or is_infinite:
            self.process_single_measure(is_all_full_year)
        else:
            self.process_measure_list(is_all_full_year, is_infinite)

    def process_single_measure(self, is_all_full_year):
        if not self.measure_list:
            return

        self.measure_list = self.measure_list[:1]
        measure = self.measure_list[0]

        self.duty_string += measure.xml_without_dates()

        if not is_all_full_year or not measure.validity_end_date:
            return

        if measure.validity_end_date < self.date_brexit.date():
            self.suppress = True

    def get_partial_period_list(self):
        partial_period_list = []

        for m in self.measure_list:
            if m.period_start:
                obj = m.period_start
                obj_split = obj.split("/")
                obj_period = Period(int(obj_split[0]), int(obj_split[1]))
                partial_period_list.append(obj_period)
        return list(set(partial_period_list))

    def process_measure_list(self, is_all_full_year, is_infinite):
        self.measure_list.reverse()

        partial_period_list = self.get_partial_period_list()

        if not is_all_full_year and not is_infinite:
            self.mark_measure(partial_period_list)

        for i in range(len(self.measure_list) - 1, 0, -1):
            measure = self.measure_list[i]
            if measure.suppress:
                self.measure_list.pop(i)

        # Before finally writing the items to a list, we need to look at contiguous items
        # that have the same duty and combine
        self.measure_list.reverse()
        self.compare_measures()

        # A final check that this concatenation of measures has
        # not actually generated a single measure
        # This is the case with product 0702000000 for Palestine, also Canada

        if len(self.measure_list) == 1:
            m = self.measure_list[0]
            if m.validity_end_date < self.date_brexit.date():
                logger.debug(f"Found a single measure that ends before Brexit {self.commodity_code}")
                self.suppress = True

            if m.extent in (365, 366, -1):
                self.duty_string = m.xml_without_dates() + self.duty_string
            else:
                self.duty_string = m.xml_with_dates() + self.duty_string
        else:
            for measure in self.measure_list:
                self.duty_string += measure.xml_with_dates()

    def compare_measures(self):
        for i in range(len(self.measure_list) - 2, -1, -1):
            m1 = self.measure_list[i]
            m2 = self.measure_list[i + 1]
            # if m1 finished a day before m2 starts
            delta = (m2.validity_start_date - m1.validity_end_date).days
            if (delta == 1) and (m1.combined_duty == m2.combined_duty):
                m1.period_end = m2.period_end
                m1.period = m1.period_start + " to " + m1.period_end
                m1.validity_end_date = m2.validity_end_date
                m1.extent = (m1.validity_end_date - m1.validity_start_date).days + 1
                self.measure_list.pop(i + 1)
