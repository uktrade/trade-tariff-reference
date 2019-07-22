import trade_tariff_reference.documents.fta.functions as functions


PLUS_PREFIX = '+ '
MIN_PREFIX = 'MIN '
MAX_PREFIX = 'MAX '


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
        self.duty_amount = duty_amount or 0
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
        if self.is_siv:
            return self.get_siv_duty_string()

        simple_duty_dict = {
            '12': ' + AC',
            '14': ' + ACR',
            '21': ' + SD',
            '25': ' + SDR',
            '27': ' + FD',
            '29': ' + FDR',
        }

        simple_duty = simple_duty_dict.get(self.duty_expression_id)
        if simple_duty:
            return simple_duty

        prefix_dict = {
            '01': '',
            '04': PLUS_PREFIX,
            '19': PLUS_PREFIX,
            '20': PLUS_PREFIX,
            '15': MIN_PREFIX,
            '17': MAX_PREFIX,
            '35': MAX_PREFIX,
        }

        prefix = prefix_dict.get(self.duty_expression_id)

        if prefix is None:
            return ""

        if not self.monetary_unit_code:
            return f"{prefix}{self.duty_amount:1.2f}%"

        duty_string = f"{prefix}{self.duty_amount:1.3f} {self.monetary_unit_code}"
        if self.measurement_unit_code:
            duty_string += f" / {self.get_measurement_unit(self.measurement_unit_code)}"
            if self.measurement_unit_qualifier_code:
                duty_string += f" / {self.get_qualifier()}"
        return duty_string

    def get_siv_duty_string(self):
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

        siv_duty_amount = 0

        if self.duty_amount > 0:
            mfn_rate = self.application.get_mfn_rate(self.commodity_code, self.validity_start_date)
            if mfn_rate:
                siv_duty_amount = (self.duty_amount / mfn_rate) * 100

        rebased_price = ""
        if (
            self.commodity_code in self.application.local_sivs_commodities_only
            and self.application.country_profile == "morocco"
        ):
            rebased_price = self.get_rebased_price_string()

        return f"Entry Price - {siv_duty_amount:1.2f}% + Specific 100%{rebased_price}"

    def get_rebased_price_string(self):
        out = ""
        for obj in self.application.local_sivs:
            if obj.goods_nomenclature_item_id != self.commodity_code:
                continue
            elif self.validity_start_date == obj.validity_start_date:
                units = self.get_measurement_unit(obj.condition_measurement_unit_code)  # "tonne"
                return f" Rebased Price {obj.condition_duty_amount} € / {units}"
        return out

    def get_measurement_unit(self, abbreviation):
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
        return units_dict.get(abbreviation, abbreviation)

    def get_qualifier(self):
        qualifier_dict = {
            'A': 'tot alc',
            'C': '1 000',
            'E': 'net drained wt',
            'G': 'gross',
            'M': 'net dry',
            'P': 'lactic matter',
            'R': 'std qual',
            'S': 'raw sugar',
            'T': 'dry lactic matter',
            'X': 'hl',
            'Z': '% sacchar.',
        }
        return qualifier_dict.get(self.measurement_unit_qualifier_code, '')
