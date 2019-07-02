import documents.fta.functions as f


class QuotaDefinition:

    def __init__(
        self, quota_definition_sid, quota_order_number_id, validity_start_date, validity_end_date,
        quota_order_number_sid, volume, initial_volume, measurement_unit_code, maximum_precision,
        critical_state, critical_threshold, monetary_unit_code, measurement_unit_qualifier_code
    ):
        self.quota_definition_sid = quota_definition_sid
        self.quota_order_number_id = quota_order_number_id
        self.validity_start_date = validity_start_date
        self.validity_end_date = validity_end_date
        self.quota_order_number_sid = quota_order_number_sid
        self.volume = volume
        self.initial_volume = initial_volume
        self.measurement_unit_code = measurement_unit_code
        self.maximum_precision = maximum_precision
        self.critical_state = critical_state
        self.critical_threshold = critical_threshold
        self.monetary_unit_code = monetary_unit_code
        self.measurement_unit_qualifier_code = measurement_unit_qualifier_code

        self.volume_yx = 0
        self.formatted_initial_volume = ""
        self.formatted_volume_yx = ""
        self.addendum = ""
        self.scope = ""

    def format_volumes(self):
        self.formatted_initial_volume = self.format_volume(self.initial_volume)
        self.formatted_volume_yx = self.format_volume(self.volume_yx)

    def format_volume(self, val):
        try:
            s = "{:,.0f}".format(val) + " " + f.getMeasurementUnit(self.measurement_unit_code)
        except:
            s = ""
        if self.measurement_unit_qualifier_code != None:
            s += " " + self.measurement_unit_qualifier_code

        s = s.strip()
        return s