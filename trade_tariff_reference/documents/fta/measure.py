from datetime import datetime, timedelta


class Measure:

    def __init__(
        self,
        measure_sid,
        commodity_code,
        quota_order_number_id,
        validity_start_date,
        validity_end_date,
        geographical_area_id,
        reduction_indicator
    ):
        # Get parameters from instantiator
        self.measure_sid = measure_sid
        self.commodity_code = commodity_code
        self.quota_order_number_id = quota_order_number_id
        self.validity_start_date = validity_start_date
        self.validity_end_date = validity_end_date
        self.reduction_indicator = reduction_indicator
        self.old_duties = []

        self.validity_start_day = datetime.strftime(self.validity_start_date, "%d")
        self.validity_start_month = datetime.strftime(self.validity_start_date, "%m")
        self.validity_start_year = datetime.strftime(self.validity_start_date, "%Y")

        if self.validity_end_date is not None:
            self.extent = (self.validity_end_date - self.validity_start_date).days + 1
            self.validity_end_day = datetime.strftime(self.validity_end_date, "%d")
            self.validity_end_month = datetime.strftime(self.validity_end_date, "%m")
            self.validity_end_year = datetime.strftime(self.validity_end_date, "%Y")
            self.period_start = str(self.validity_start_day).zfill(2) + "/" + str(self.validity_start_month).zfill(2)
            self.period_end = str(self.validity_end_day).zfill(2) + "/" + str(self.validity_end_month).zfill(2)
            self.period = self.period_start + " to " + self.period_end
        else:
            self.extent = -1
            self.validity_end_day = 0
            self.validity_end_month = 0
            self.validity_end_year = 0
            self.period_start = ""
            self.period_end = ""
            self.period = ""

        self.geographical_area_id = geographical_area_id

        self.assigned = False
        self.combined_duty = ""
        self.duty_list = []
        self.suppress = False
        self.marked = False
        self.seasonal_list = []
        self.is_siv = False

    def xml_without_dates(self):
        return "<w:r><w:t>" + self.combined_duty + "</w:t></w:r>"

    def xml_with_dates(self):
        whitespace = "<w:tab/>"
        s = "<w:r><w:t>"
        s += self.period
        # s += str(self.validity_start_day).zfill(2) + "/" + str(self.validity_start_month).zfill(2)
        # s += " to "
        # s += str(self.validity_end_day).zfill(2) + "/" + str(self.validity_end_month).zfill(2)
        s += "</w:t></w:r><w:r>" + whitespace + "<w:t>" + self.combined_duty + "</w:t></w:r>"
        s += "<w:r><w:br/></w:r>"
        return s

    def combine_duties(self, application):
        combined_duty = self.get_duty_string(self.duty_list)
        if self.old_duties and self.validity_start_date >= datetime(2019, 11, 1, 0, 0):
            old_duty = self.get_duty_string(self.filtered_old_duties())
            if old_duty != combined_duty and old_duty != '':
                combined_duty = old_duty
        self.combined_duty = self._combine_duties(combined_duty, application)

    def filtered_old_duties(self):
        duties = []
        last_year = self.validity_start_date - timedelta(days=365)
        for duty in self.old_duties:
            if (last_year >= duty.validity_start_date) and (last_year <= duty.validity_end_date):
                duties.append(duty)
        return duties

    def get_duty_string(self, duty_list):
        combined_duty = ""
        for d in duty_list:
            combined_duty += d.duty_string + " "
        combined_duty = combined_duty.replace("  ", " ")
        return combined_duty.strip()

    def _combine_duties(self, combined_duty, application):
        # Now add in the Meursing components
        if "ACR" in combined_duty or "SDR" in combined_duty or "FDR" in combined_duty:
            # print("Reduction indicator", self.reduction_indicator)
            meursing_percentage = application.get_meursing_percentage(
                self.reduction_indicator,
                self.geographical_area_id
            )
            combined_duty = "CAD - " + combined_duty + ") " + str(meursing_percentage) + "%"
            combined_duty = combined_duty.replace(" + ", " + (", 1)
            combined_duty = combined_duty.replace("ACR", "AC")
            combined_duty = combined_duty.replace("FDR", "FD")
            combined_duty = combined_duty.replace("SDR", "SD")

        # Now add in the Meursing components
        elif "AC" in combined_duty or "SD" in combined_duty or "FD" in combined_duty:
            combined_duty = "CAD - " + combined_duty + ") 100%"
            combined_duty = combined_duty.replace(" + ", " + (", 1)

        return combined_duty


class Period:

    def __init__(self, validity_start_day, validity_start_month):
        self.validity_start_day = validity_start_day
        self.validity_start_month = validity_start_month
        self.marked = False
