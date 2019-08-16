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
        self.get_duty_string()

    def get_duty_string(self):
        self.duty_string = ""
        qualifier_description = functions.get_measurement_unit_qualifier_code(self.measurement_unit_qualifier_code)

        if self.duty_expression_id == "01":  # Ad valorem of specific
            if self.monetary_unit_code == "":
                self.duty_string += "{0:1.1f}".format(self.duty_amount) + "%"
            else:
                self.duty_string += "{0:1.3f}".format(self.duty_amount) + " " + self.monetary_unit_code
                if self.measurement_unit_code != "":
                    self.duty_string += " / " + functions.get_measurement_unit(self.measurement_unit_code)
                    if self.measurement_unit_qualifier_code != "":
                        self.duty_string += " / " + qualifier_description

        elif self.duty_expression_id in ("04", "19", "20"):  # Plus % or amount
            if self.monetary_unit_code == "":
                self.duty_string += "+ {0:1.1f}".format(self.duty_amount) + "%"
            else:
                self.duty_string += "+ {0:1.3f}".format(self.duty_amount) + " " + self.monetary_unit_code
                if self.measurement_unit_code != "":
                    self.duty_string += " / " + functions.get_measurement_unit(self.measurement_unit_code)
                    if self.measurement_unit_qualifier_code != "":
                        self.duty_string += " / " + qualifier_description

        elif self.duty_expression_id == "12":  # Agri component
            self.duty_string += " + AC"

        elif self.duty_expression_id == "15":  # Minimum
            if self.monetary_unit_code == "":
                self.duty_string += "MIN {0:1.1f}".format(self.duty_amount) + "%"
            else:
                self.duty_string += "MIN {0:1.3f}".format(self.duty_amount) + " " + self.monetary_unit_code
                if self.measurement_unit_code != "":
                    self.duty_string += " / " + functions.get_measurement_unit(self.measurement_unit_code)
                    if self.measurement_unit_qualifier_code != "":
                        self.duty_string += " / " + qualifier_description

        elif self.duty_expression_id == "17":  # Maximum
            if self.monetary_unit_code == "":
                self.duty_string += "MAX {0:1.1f}".format(self.duty_amount) + "%"
            else:
                self.duty_string += "MAX {0:1.3f}".format(self.duty_amount) + " " + self.monetary_unit_code
                if self.measurement_unit_code != "":
                    self.duty_string += " / " + functions.get_measurement_unit(self.measurement_unit_code)
                    if self.measurement_unit_qualifier_code != "":
                        self.duty_string += " / " + qualifier_description

        elif self.duty_expression_id == "21":  # Sugar duty
            self.duty_string += " + SD"

        elif self.duty_expression_id == "27":  # Flour duty
            self.duty_string += " + FD"
