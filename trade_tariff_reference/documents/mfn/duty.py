from trade_tariff_reference.documents import functions


class Duty:

    def __init__(
        self, commodity_code="", additional_code_type_id="", additional_code_id="", measure_type_id="",
        duty_expression_id="", duty_amount=0, monetary_unit_code="", measurement_unit_code="",
        measurement_unit_qualifier_code="", measure_sid=0
    ):
        self.commodity_code = functions.mstr(commodity_code)
        self.additional_code_type_id = functions.mstr(additional_code_type_id)
        self.additional_code_id = functions.mstr(additional_code_id)
        self.measure_type_id = functions.mstr(measure_type_id)
        self.measure_type_description = ""
        self.duty_expression_id = functions.mstr(duty_expression_id)
        self.duty_amount = duty_amount
        self.monetary_unit_code = functions.mstr(monetary_unit_code)
        self.measurement_unit_code = functions.mstr(measurement_unit_code)
        self.measurement_unit_qualifier_code = functions.mstr(measurement_unit_qualifier_code)
        self.measure_sid = measure_sid
        self.duty_string = self.get_duty_string()

    def get_duty_string_additional_abbreviation(self):
        additional_abbreviation_dict = {
            '12': 'AC',
            '21': 'SD',
            '27': 'FD',
        }
        abbreviation = additional_abbreviation_dict.get(
            self.duty_expression_id
        )
        if abbreviation:
            return f' + {abbreviation}'
        return

    def get_duty_string_prefix(self):
        prefix_dict = {
            '04': '+ ',
            '19': '+ ',
            '20': '+ ',
            '15': 'MIN ',
            '17': 'MAX ',
        }
        return prefix_dict.get(self.duty_expression_id, '')

    def get_duty_string_suffix(self):
        if not self.measurement_unit_code:
            return ''
        qualifier_description = ''
        if self.measurement_unit_qualifier_code:
            qualifier_description = functions.get_measurement_unit_qualifier_code(
                self.measurement_unit_qualifier_code
            )
            qualifier_description = f' / {qualifier_description}'
        return f' / {functions.get_measurement_unit(self.measurement_unit_code)}{qualifier_description}'

    def get_duty_string(self):
        additional_abbreviation = self.get_duty_string_additional_abbreviation()
        if additional_abbreviation:
            return additional_abbreviation

        if self.duty_expression_id not in ['01', '04', '12', '15', '17', '19', '20', '21', '27']:
            return ''

        prefix = self.get_duty_string_prefix()

        if self.monetary_unit_code == "":
            return f'{prefix}{self.duty_amount:1.2f}%'

        suffix = self.get_duty_string_suffix()

        return f'{prefix}{self.duty_amount:1.3f} {self.monetary_unit_code}{suffix}'
