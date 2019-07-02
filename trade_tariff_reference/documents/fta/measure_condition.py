
class MeasureCondition:

    def __init__(
        self, measure_condition_sid, measure_sid, condition_code, component_sequence_number,
        condition_duty_amount, condition_monetary_unit_code, condition_measurement_unit_code,
        condition_measurement_unit_qualifier_code, action_code, certificate_type_code,
        certificate_code
    ):

        # from parameters
        self.measure_condition_sid = measure_condition_sid
        self.measure_condition_sid_original = measure_condition_sid
        self.measure_sid = measure_sid
        self.condition_code = condition_code
        self.component_sequence_number = component_sequence_number
        self.condition_duty_amount = condition_duty_amount
        self.condition_monetary_unit_code = condition_monetary_unit_code
        self.condition_measurement_unit_code = condition_measurement_unit_code
        self.condition_measurement_unit_qualifier_code = condition_measurement_unit_qualifier_code
        self.action_code = action_code
        self.certificate_type_code = certificate_type_code
        self.certificate_code = certificate_code
        self.action = ""
