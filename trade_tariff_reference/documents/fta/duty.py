import documents.fta.functions as functions


class Duty:

    def __init__(
        self, application, commodity_code, additional_code_type_id, additional_code_id, measure_type_id,
        duty_expression_id, duty_amount, monetary_unit_code, measurement_unit_code, measurement_unit_qualifier_code,
        measure_sid, quota_order_number_id, geographical_area_id, validity_start_date, validity_end_date,
        reduction_indicator, is_siv,
    ):
        self.application = application
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
        self.quota_order_number_id = quota_order_number_id
        self.siv_duty = False
        self.geographical_area_id = geographical_area_id
        self.validity_start_date = validity_start_date
        self.validity_end_date = validity_end_date
        self.reduction_indicator = reduction_indicator
        self.is_siv = is_siv

        self.duty_string = self.get_duty_string()

    def get_duty_string(self):
        duty_string = ""

        if self.duty_expression_id == "01":
            if self.monetary_unit_code == "":
                duty_string += "{0:1.2f}".format(self.duty_amount) + "%"
            else:
                duty_string += "{0:1.3f}".format(self.duty_amount) + " " + self.monetary_unit_code
                if self.measurement_unit_code != "":
                    duty_string += " / " + self.get_measurement_unit(self.measurement_unit_code)
                    if self.measurement_unit_qualifier_code != "":
                        duty_string += " / " + self.get_qualifier()

        elif self.duty_expression_id in ("04", "19", "20"):
            if self.monetary_unit_code == "":
                duty_string += "+ {0:1.2f}".format(self.duty_amount) + "%"
            else:
                duty_string += "+ {0:1.3f}".format(self.duty_amount) + " " + self.monetary_unit_code
                if self.measurement_unit_code != "":
                    duty_string += " / " + self.get_measurement_unit(self.measurement_unit_code)
                    if self.measurement_unit_qualifier_code != "":
                        duty_string += " / " + self.get_qualifier()

        elif self.duty_expression_id == "15":
            if self.monetary_unit_code == "":
                duty_string += "MIN {0:1.2f}".format(self.duty_amount) + "%"
            else:
                duty_string += "MIN {0:1.3f}".format(self.duty_amount) + " " + self.monetary_unit_code
                if self.measurement_unit_code != "":
                    duty_string += " / " + self.get_measurement_unit(self.measurement_unit_code)
                    if self.measurement_unit_qualifier_code != "":
                        duty_string += " / " + self.get_qualifier()

        elif self.duty_expression_id in ("17", "35"):  # MAX
            if self.monetary_unit_code == "":
                duty_string += "MAX {0:1.2f}".format(self.duty_amount) + "%"
            else:
                duty_string += "MAX {0:1.3f}".format(self.duty_amount) + " " + self.monetary_unit_code
                if self.measurement_unit_code != "":
                    duty_string += " / " + self.get_measurement_unit(self.measurement_unit_code)
                    if self.measurement_unit_qualifier_code != "":
                        duty_string += " / " + self.get_qualifier()

        elif self.duty_expression_id in ("12"):
            duty_string += " + AC"

        elif self.duty_expression_id in ("14"):
            duty_string += " + ACR"

        elif self.duty_expression_id in ("21"):
            duty_string += " + SD"

        elif self.duty_expression_id in ("25"):
            duty_string += " + SDR"

        elif self.duty_expression_id in ("27"):
            duty_string += " + FD"

        elif self.duty_expression_id in ("29"):
            duty_string += " + FDR"

        else:
            print("Found an unexpected DE", self.duty_expression_id)

        if self.is_siv:
            # Still need to get the MFN duty for the same time period to work out the specific percentage
            # The phrase required here is:
            #
            # Entry Price - 6.40% + Specific 100%
            #
            # where the calculation is "((My advalorem) / (MFN ad valorem)) * 100"
            # where the "My advalorem" is zero, then this will always be zero
            # but, in the example of Israel, where, on product 0805 10 24, there is a variable ad valorem
            # including 6.4, against a 3rd country duty (MFN) of 16%, so the 1st percentage is
            # (6.4 / 16) * 100 = 40%
            # try:

            # print(g.app.DBASE)

            if not self.duty_amount:
                self.duty_amount = 0
            if self.duty_amount > 0:
                mfn_rate = self.application.get_mfn_rate(
                    self.commodity_code, self.validity_start_date, self.validity_end_date
                )
                # if self.commodity_code == "0805290011":
                # print(self.commodity_code, self.validity_start_date,
                # self.validity_end_date, self.duty_amount,  mfn_rate)
                if mfn_rate != 0.0:
                    my_duty = (self.duty_amount / mfn_rate) * 100
                else:
                    my_duty = 0
            else:
                my_duty = 0

            if (
                self.commodity_code in self.application.local_sivs_commodities_only
                and self.application.country_profile == "morocco"
            ):
                # duty_string = "Entry Price - 0% + Specific 100% Rebased price €" +
                # "{0:1.2f}".format(my_duty) + " Rebased Price P"
                duty_string = (
                    "Entry Price - " + "{0:1.2f}".format(my_duty) + "% + Specific 100%" + self.get_rebase()
                )   # " Rebased Price P"
            else:
                duty_string = "Entry Price - " + "{0:1.2f}".format(my_duty) + "% + Specific 100%"
        return duty_string

    def get_rebase(self):
        out = ""
        for obj in self.application.local_sivs:
            if obj.goods_nomenclature_item_id == self.commodity_code:
                if self.validity_start_date == obj.validity_start_date:
                    units = self.get_measurement_unit(obj.condition_measurement_unit_code)  # "tonne"
                    out = " Rebased Price " + str(obj.condition_duty_amount) + " € / " + units
                    break
        return out

    def get_measurement_unit(self, s):
        units_dict = {
            'ASV': '% vol',
            'NAR': 'item',
            'CCT': 'ct/l',
            'CEN': '100 p/st',
            'CTM': 'c/k',
            'DTN': '100 kg',
            'GFI': 'gi F/S',
            'GRM': 'g',
            'HLT': 'hl',
            'HMT': '100 m',
            'KGM': 'kg',
            'KLT': '1,000 l',
            'KMA': 'kg met.am.',
            'KNI': 'kg N',
            'KNS': 'kg H202',
            'KPH': 'kg KOH',
            'KPO': 'kg K20',
            'KPP': 'kg P205',
            'KSD': 'kg 90 % sdt',
            'KSH': 'kg NaOH',
            'KUR': 'kg U',
            'LPA': 'l alc. 100%',
            'LTR': 'l',
            'MIL': '1,000 items',
            'MTK': 'm2',
            'MTQ': 'm3',
            'MTR': 'm',
            'MWH': '1,000 kWh',
            'NCL': 'ce/el',
            'NPR': 'pa',
            'TJO': 'TJ',
            'TNE': 'tonne',
        }
        return units_dict.get(s, s)

    def get_qualifier(self):
        qualifier_dict = {
            'A': 'tot alc',
            'C': '1 000',
            'E': 'net drained wt',
            'G': 'gross',
            'M': 'net dry',
            'P': 'lactic matter',
            'R': 'std qual',
            'S': ' raw sugar',
            'T': 'dry lactic matter',
            'X': ' hl',
            'Z': '% sacchar.',
        }
        return qualifier_dict.get(self.measurement_unit_qualifier_code, '')
