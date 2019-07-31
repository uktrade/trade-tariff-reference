import trade_tariff_reference.documents.fta.functions as f


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
        self.measurement_unit_code = measurement_unit_code or ""
        self.maximum_precision = maximum_precision
        self.critical_state = critical_state
        self.critical_threshold = critical_threshold
        self.monetary_unit_code = monetary_unit_code or ""
        self.measurement_unit_qualifier_code = measurement_unit_qualifier_code or ""

        self.volume_yx = 0
        self.formatted_initial_volume = self.format_volume(self.initial_volume)
        self.formatted_volume_yx = self.format_volume(self.volume_yx)
        self.addendum = ""
        self.scope = ""

    def format_volume(self, volume):
        try:
            formatted_string = (
                f"{volume:,.0f} {f.get_measurement_unit(self.measurement_unit_code)}"
                f" {self.measurement_unit_qualifier_code}"
            )
        except:
            formatted_string = ""

        formatted_string = formatted_string.strip()
        return formatted_string

    def format_volumes(self):
        # MPP: TODO Look in to when this called as removing the
        # individual calls from document.py changes the file generated
        self.formatted_initial_volume = self.format_volume(self.initial_volume)
        self.formatted_volume_yx = self.format_volume(self.volume_yx)
