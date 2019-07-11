import documents.fta.functions as functions
from documents.fta.measure import Period


class QuotaCommodity:

    def __init__(self, commodity_code, quota_order_number_id):
        self.commodity_code = functions.mstr(commodity_code)
        self.quota_order_number_id = functions.mstr(quota_order_number_id)
        self.measure_list = []
        self.duty_string = ""
        self.suppress = False
        self.commodity_code_formatted = self.format_commodity_code()

    def resolve_measures(self):
        self.duty_string = ""

        is_all_full_year = True
        contains_siv = False
        is_infinite = False

        for measure in self.measure_list:
            # if self.commodity_code == "0204230011":
            # print(len(self.measure_list), "jijij")
            if measure.extent not in(365, -1):
                is_all_full_year = False

            if measure.extent == -1:
                is_infinite = True

            if "Entry Price" in measure.combined_duty:
                contains_siv = True

            # if self.commodity_code == "0204230011":
            # print("QQQQQQQQQQQQQQQQQQQQQQ", Measure.extent, self.commodity_code, is_all_full_year)

        # Check for EU screw-ups where they restarted a Measure for no reason
        # List all of the measures, remove the measures that are 365 days long
        # Then add the other ones up: if they add up to 365, then treat this as a whole year Measure
        temp_measure_list = []
        for measure in self.measure_list:
            if measure.extent != 365:
                temp_measure_list.append(measure)

        day_count = 0
        for measure in temp_measure_list:
            day_count += measure.extent

        if day_count == 365:
            is_all_full_year = True

        # Check to see if this is a full year Measure

        # If it is, then only show the chronologically last Duty, as any others will be from a previous year
        # Also check to see if this is on the entry price system. If this is EPS, then it is not going to
        # be seasonal as well - they appear to be mutually exclusive

        if is_all_full_year or contains_siv:
            measure_count = len(self.measure_list)

            if measure_count > 0:
                for i in range(0, measure_count):
                    if i != measure_count - 1:
                        measure = self.measure_list[i]
                        measure.suppress = True

        # So if the Measure is neither infinite, nor entry price, nor is it a full year Measure
        # Then it must be seasonal
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

        reversed_list = self.measure_list
        reversed_list.reverse()

        is_seasonal = False
        if not contains_siv and not is_all_full_year and not is_infinite:
            is_seasonal = True
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

        for measure in self.measure_list:
            if not measure.suppress:
                if is_seasonal:
                    self.duty_string = measure.combined_duty
                else:
                    self.duty_string += measure.combined_duty

        # if self.duty_string == "":
        # print("Duty string is erroneously blank", self.commodity_code)

    def format_commodity_code(self):
        end_values = self.commodity_code[8:10]
        if end_values == '00':
            end_values = ''

        formatted_string = (
            f'{self.commodity_code[0:4]} {self.commodity_code[4:6]}'
            f' {self.commodity_code[6:8]} {end_values}'
        )
        formatted_string = formatted_string.strip()
        return formatted_string