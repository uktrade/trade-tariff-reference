from datetime import datetime
import os
import re
import csv
import codecs

import documents.fta.functions as f

from documents.fta.constants import *
from documents.fta.duty import Duty
from documents.fta.quota_order_number import QuotaOrderNumber
from documents.fta.quota_definition import QuotaDefinition
from documents.fta.measure import Measure
from documents.fta.measure_condition import MeasureCondition
from documents.fta.commodity import Commodity
from documents.fta.quota_commodity import QuotaCommodity
from documents.fta.quota_balance import QuotaBalance


class Document:

    def __init__(self, application):
        self.application = application
        self.footnote_list = []
        self.duty_list = []
        self.balance_list = []
        self.supplementary_unit_list = []
        self.seasonal_records = 0
        self.wide_duty = False

        f.log("Creating FTA document for " + application.country_name + "\n")
        self.application.get_mfns_for_siv_products()

        self.document_xml = ""

    def check_for_quotas(self):
        rows = self.application.execute_sql(
            GET_QUOTA_ORDER_NUMBERS_SQL.format(geo_ids=self.application.geo_ids)
        )
        if len(rows) == 0:
            f.log(" - This FTA has no quotas")
            result = False
        else:
            f.log(" - This FTA has quotas")
            result = True
        self.has_quotas = result
        return result

    def get_measure_type_list_for_instrument_type(self, instrument_type):
        if instrument_type == "preferences":
            return "'142', '145'"
        return "'143', '146'"

    def get_measure_conditions(self, measure_type_list):
        measure_condition_list = []

        rows = self.application.execute_sql(
            GET_MEASURE_COMPONENTS_SQL.format(measure_type_list=measure_type_list, geo_ids=self.application.geo_ids),
            dict_cursor=True
        )
        for row in rows:
            mc = MeasureCondition(0, row['measure_sid'], "V", 1, row['duty_amount'], "", "", "", "", "", "")
            measure_condition_list.append(mc)
        return measure_condition_list

    def get_exclusion_list(self):
        exclusion_list = []

        if not self.application.exclusion_check:
            return exclusion_list

        rows = self.application.execute_sql(
            CHECK_COUNTRY_EXCLUSION_SQL.format(exclusion_check=self.application.exclusion_check), dict_cursor=True
        )

        return [row['measure_sid'] for row in rows]

    def _get_duties(self, measure_type_list):
        return self.application.execute_sql(
            GET_DUTIES_SQL.format(measure_type_list=measure_type_list, geo_ids=self.application.geo_ids)
        )

    def get_duties(self, instrument_type):
        f.log(" - Getting duties for " + instrument_type)

        ###############################################################
        # Work out which measures to capture
        measure_type_list = self.get_measure_type_list_for_instrument_type(instrument_type)

        ###############################################################
        # Before getting the duties, get the measure component conditions
        # These are used in adding in SIV components whenever the duty is no present
        # due to the fact that there are SIVs applied via measure components
        f.log(" - Getting measure conditions")
        measure_condition_list = self.get_measure_conditions(measure_type_list)

        # Now get the country exclusions
        exclusion_list = self.get_exclusion_list()

        # Get the duties (i.e the measure components)
        # Add this back in for Switzerland ( OR m.measure_sid = 3231905)

        duties = self._get_duties(measure_type_list)

        # Do a pass through the duties table and create a
        # full Duty expression - Duty is a mnemonic for Measure component
        temp_commodity_list = []
        temp_quota_order_number_list = []
        temp_measure_list = []
        self.duty_list = []
        self.measure_list = []
        self.commodity_list = []
        self.quota_order_number_list = []

        for row in duties:
            measure_sid = row[9]
            if measure_sid not in exclusion_list:
                commodity_code = f.mstr(row[0])
                additional_code_type_id = f.mstr(row[1])
                additional_code_id = f.mstr(row[2])
                measure_type_id = f.mstr(row[3])
                duty_expression_id = row[4]
                duty_amount = row[5]
                monetary_unit_code = f.mstr(row[6])
                monetary_unit_code = monetary_unit_code.replace("EUR", "€")
                measurement_unit_code = f.mstr(row[7])
                measurement_unit_qualifier_code = f.mstr(row[8])
                quota_order_number_id = f.mstr(row[10])
                validity_start_date = row[11]
                validity_end_date = row[12]
                geographical_area_id = f.mstr(row[13])
                reduction_indicator = row[14]

                # Hypothesis would be that the only reason why the Duty amount is None is when
                # there is a "V" code attached to the Measure
                # if ((duty_amount is None) and (duty_expression_id == "01")):
                if duty_amount is None and duty_expression_id is None:
                    is_siv = True
                    for mc in measure_condition_list:
                        # print(mc.measure_sid, measure_sid)
                        if mc.measure_sid == measure_sid:
                            duty_expression_id = "01"
                            duty_amount = mc.condition_duty_amount
                            # break
                else:
                    is_siv = False

                obj_duty = Duty(
                    self.application, commodity_code, additional_code_type_id, additional_code_id, measure_type_id,
                    duty_expression_id, duty_amount, monetary_unit_code, measurement_unit_code,
                    measurement_unit_qualifier_code, measure_sid, quota_order_number_id, geographical_area_id,
                    validity_start_date, validity_end_date, reduction_indicator, is_siv
                )
                self.duty_list.append(obj_duty)

                if measure_sid not in temp_measure_list:
                    obj_measure = Measure(
                        measure_sid, commodity_code, quota_order_number_id, validity_start_date, validity_end_date,
                        geographical_area_id, reduction_indicator
                    )
                    self.measure_list.append(obj_measure)
                    temp_measure_list.append(measure_sid)

                if commodity_code not in temp_commodity_list:
                    obj_commodity = Commodity(commodity_code)
                    self.commodity_list.append(obj_commodity)
                    temp_commodity_list.append(commodity_code)

                if quota_order_number_id not in temp_quota_order_number_list:
                    if quota_order_number_id != "":
                        obj_quota_order_number = QuotaOrderNumber(quota_order_number_id)
                        self.quota_order_number_list.append(obj_quota_order_number)
                        temp_quota_order_number_list.append(quota_order_number_id)

        self.assign_duties_to_measures()
        self.assign_measures_to_commodities()
        self.combine_duties()
        self.resolve_measures()

    def assign_duties_to_measures(self):
        # Loop through the measures and assign duties to them
        for m in self.measure_list:
            for d in self.duty_list:
                if m.measure_sid == d.measure_sid:
                    m.duty_list.append(d)

    def assign_measures_to_commodities(self):
        # Loop through the commodities and assign measures to them
        for c in self.commodity_list:
            for m in self.measure_list:
                if m.commodity_code == c.commodity_code:
                    c.measure_list.append(m)

    def combine_duties(self):
        # Combine duties into a string
        for m in self.measure_list:
            m.combine_duties(self.application)

    def resolve_measures(self):
        # Finally, form the measures into a consolidated string
        for c in self.commodity_list:
            c.resolve_measures()

    def get_quota_order_numbers(self):
        f.log(" - Getting unique quota order numbers")
        # Get unique order numbers

        rows = self.application.execute_sql(
            GET_QUOTA_ORDER_NUMBERS_SQL.format(geo_ids=self.application.geo_ids),
        )
        if len(rows) == 0:
            self.has_quotas = False
            return
        else:
            self.has_quotas = True

        self.quota_order_number_list = []
        self.q = []
        quota_order_number_list_flattened = ""
        csv_text = ""
        for row in rows:
            quota_order_number_id = row[0]
            qon = QuotaOrderNumber(quota_order_number_id)
            self.quota_order_number_list.append(qon)
            self.q.append(quota_order_number_id)
            quota_order_number_list_flattened += "'" + quota_order_number_id + "',"
            csv_text += quota_order_number_id + "\n"

        quota_order_number_list_flattened = quota_order_number_list_flattened.strip()
        quota_order_number_list_flattened = quota_order_number_list_flattened.strip(",")

        # Get the partial temporary stops, so that we can omit the suspended measures
        filename = os.path.join(self.application.CSV_DIR, self.application.country_profile + "_quotas.csv")
        file = codecs.open(filename, "w", "utf-8")
        file.write(csv_text)
        file.close()

    def get_quota_measures(self):
        # print(len(self.commodity_list))
        # Get the measures - in order to get the commodity codes and the duties
        # Just get the commodities and add to an array
        rows = self.application.execute_sql(
            GET_QUOTA_MEASURES_SQL.format(geo_ids=self.application.geo_ids),
        )
        if len(rows) == 0:
            self.has_quotas = False
            return

        self.measure_list = []
        for row in rows:
            measure_sid = row[0]
            goods_nomenclature_item_id = row[1]
            quota_order_number_id = row[2]
            validity_start_date = row[3]
            validity_end_date = row[4]
            geographical_area_id = row[5]
            reduction_indicator = row[6]

            my_measure = Measure(
                measure_sid, goods_nomenclature_item_id, quota_order_number_id, validity_start_date, validity_end_date,
                geographical_area_id, reduction_indicator
            )
            self.measure_list.append(my_measure)

        # Step 2 - Having loaded all of the measures from the database, cycle through the list of duties (components)
        # previously loaded and assign to the measures where appropriate
        temp_commodity_list = []
        for my_measure in self.measure_list:
            for d in self.duty_list:
                if int(my_measure.measure_sid) == int(d.measure_sid):
                    my_measure.duty_list.append(d)
                    my_measure.assigned = True
                    temp_commodity_list.append(my_measure.commodity_code + "|" + my_measure.quota_order_number_id)

            my_measure.combine_duties(self.application)

        # Step 3 - Create commodity objects that relate all of the measures together
        temp_commodity_set = set(temp_commodity_list)
        quota_commodity_list = []
        for item in temp_commodity_set:
            item_split = item.split("|")
            code = item_split[0]
            quota_order_number_id = item_split[1]
            obj = QuotaCommodity(code, quota_order_number_id)
            quota_commodity_list.append(obj)

        quota_commodity_list.sort(key=lambda x: x.commodity_code, reverse=False)

        # Step 4 - Assign all relevant measures to the commodity code
        for my_commodity in quota_commodity_list:
            for my_measure in self.measure_list:
                if (
                        my_measure.commodity_code == my_commodity.commodity_code and
                        my_measure.quota_order_number_id == my_commodity.quota_order_number_id
                ):
                    my_commodity.measure_list.append(my_measure)

        for my_commodity in quota_commodity_list:
            my_commodity.resolve_measures()

        for my_commodity in quota_commodity_list:
            for qon in self.quota_order_number_list:
                if my_commodity.quota_order_number_id == qon.quota_order_number_id:
                    qon.commodity_list.append(my_commodity)
                    break

    def get_quota_balances_from_csv(self):
        f.log(" - Getting quota balances from CSV")
        if self.has_quotas is False:
            return
        with open(self.application.BALANCE_FILE, "r") as balance_file:
            reader = csv.reader(balance_file)
            temp = list(reader)
        for balance in temp:
            try:
                quota_order_number_id = balance[0].strip()
                country = balance[1]
                method = balance[2]
                y1_balance = balance[9]
                yx_balance = balance[10]
                yx_start = balance[11]
                measurement_unit_code = balance[12].strip()
                origin_quota = balance[13].strip()
                addendum = balance[14].strip()
                scope = balance[15].strip()

                if measurement_unit_code == "KGM":
                    measurement_unit_code = "KGM"

                if quota_order_number_id not in ("", "Quota order number"):
                    qb = QuotaBalance(
                        quota_order_number_id, country, method, y1_balance, yx_balance, yx_start,
                        measurement_unit_code, origin_quota, addendum, scope
                    )

                    self.balance_list.append(qb)
            except:
                pass

    def get_quota_definitions(self):
        if self.has_quotas is False:
            return

        # Now get the quota definitions - this just gets quota definitions for FCFS quota
        # Any licensed quotas with first three characters "094" needs there to be an additional step to get the balances
        # from a CSV file - as per function "get_quota_balances_from_csv" above

        my_order_numbers = f.list_to_sql(self.q)

        rows = self.application.execute_sql(
            GET_QUOTA_DEFINITIONS_SQL.format(order_numbers=my_order_numbers)
        )

        self.quota_definition_list = []
        for row in rows:
            quota_definition_sid = row[0]
            quota_order_number_id = row[1]
            validity_start_date = row[2]
            validity_end_date = row[3]
            quota_order_number_sid = row[4]
            volume = row[5]
            initial_volume = row[6]
            measurement_unit_code = row[7]
            maximum_precision = row[8]
            critical_state = row[9]
            critical_threshold = row[9]
            monetary_unit_code = row[10]
            measurement_unit_qualifier_code = row[11]

            qd = QuotaDefinition(
                quota_definition_sid, quota_order_number_id, validity_start_date, validity_end_date,
                quota_order_number_sid, volume, initial_volume, measurement_unit_code, maximum_precision,
                critical_state, critical_threshold, monetary_unit_code, measurement_unit_qualifier_code
            )

            found_matching_balance = None
            if len(self.balance_list) > 0:
                found_matching_balance = False
                for qb in self.balance_list:
                    if str(qb.quota_order_number_id) == str(qd.quota_order_number_id):
                        found_matching_balance = True
                        # print(qd.quota_order_number_id)
                        qd.initial_volume = f.mnum(qb.y1_balance)
                        qd.volume_yx = f.mnum(qb.yx_balance)
                        qd.addendum = qb.addendum
                        qd.scope = qb.scope
                        qd.format_volumes()
                        break

            if found_matching_balance is False:
                f.log(f"Matching balance not found {qd.quota_order_number_id}")
            qd.format_volumes()
            self.quota_definition_list.append(qd)

        # This process goes through the balance list (derived from the CSV) and assigns both the 2020 balance to the
        # quota definition object, as well as assigning the 2019 and 2020 balance to the licensed quotas
        # Stop press: I need to also assign the 2019 balance from the CSV, as this is a process run entirely against
        # the EU's files, not the UK's
        for qon in self.quota_order_number_list:
            if qon.quota_order_number_id[0:3] == "094":
                # For licensed quotas, we need to create a brand new (artifical, not DB-persisted)
                # definition, for use in the creation of the FTA document only
                if len(self.balance_list) > 0:
                    for qb in self.balance_list:
                        if qb.quota_order_number_id == qon.quota_order_number_id:
                            if qb.measurement_unit_code == "":
                                qb.measurement_unit_code = "KGM"
                            d1 = datetime.strptime(qb.yx_start, "%d/%m/%Y")
                            d2 = qb.yx_end
                            qd = QuotaDefinition(
                                0, qon.quota_order_number_id, d1, d2, 0, int(qb.y1_balance), int(qb.y1_balance),
                                qb.measurement_unit_code, 3, "Y", 90, "", ""
                            )
                            qd.volume_yx = int(qb.yx_balance)
                            qd.addendum = qb.addendum.strip()
                            qd.scope = qb.scope.strip()
                            qd.format_volumes()
                            self.quota_definition_list.append(qd)
                            break

        # Finally, add the quota definitions, replete with their new balances
        # to the relevant quota order numbers
        for qon in self.quota_order_number_list:
            for qd in self.quota_definition_list:
                if qd.quota_order_number_id == qon.quota_order_number_id:
                    qon.quota_definition_list.append(qd)
                    break

        # Now get the quota origins from the balance file
        for qon in self.quota_order_number_list:
            if len(self.balance_list) > 0:
                for qb in self.balance_list:
                    if qb.quota_order_number_id == qon.quota_order_number_id:
                        qon.origin_quota = qb.origin_quota
                        break

        # Now get the 2019 start date from the balance file
        for qon in self.quota_order_number_list:
            if len(self.balance_list) > 0:
                for qb in self.balance_list:
                    if qb.quota_order_number_id == qon.quota_order_number_id:
                        qon.validity_start_date_2019 = qb.validity_start_date_2019
                        # qon.validity_end_date_2019 = qb.validity_end_date_2019
                        break

    def print_quotas(self):
        f.log(" - Getting quotas")
        if self.has_quotas is False:
            self.document_xml = self.document_xml.replace("{QUOTA TABLE GOES HERE}", "")
            return
        table_content = ""

        for qon in self.quota_order_number_list:

            # Check balance info has been provided, if not then do not display
            balance_found = False
            for bal in self.balance_list:
                if bal.quota_order_number_id == qon.quota_order_number_id:
                    balance_found = True
                    break

            # if not balance_found:
            # print("Quota balance not found", qon.quota_order_number_id)

            if balance_found:
                if len(qon.quota_definition_list) > 1:
                    f.log("More than one definition - we must be in Morocco")

                if len(qon.quota_definition_list) == 0:
                    # if there are no definitions, then, either this is a screwed quota and the database is
                    # missing definition entries, or this is a licensed quota, that we have somehow missed beforehand?
                    # Check get_quota_definitions which should avoid this eventuality.
                    qon.validity_start_date = datetime.strptime("2019-03-29", "%Y-%m-%d")
                    qon.validity_end_date = datetime.strptime("2019-12-31", "%Y-%m-%d")
                    f.log(f"No quota definitions found for quota {qon.quota_order_number_id}")
                    qon.initial_volume = ""
                    qon.volume_yx = ""
                    qon.addendum = ""
                    qon.scope = ""
                    qon.measurement_unit_code = ""
                    qon.monetary_unit_code = ""
                    qon.measurement_unit_qualifier_code = ""
                else:
                    qon.validity_start_date = qon.quota_definition_list[0].validity_start_date
                    qon.validity_end_date = qon.quota_definition_list[0].validity_end_date
                    qon.validity_end_date_2019 = qon.quota_definition_list[0].validity_end_date

                    qon.initial_volume = qon.quota_definition_list[0].formatted_initial_volume
                    qon.volume_yx = qon.quota_definition_list[0].formatted_volume_yx
                    qon.addendum = qon.quota_definition_list[0].addendum
                    qon.scope = qon.quota_definition_list[0].scope
                    qon.measurement_unit_code = qon.quota_definition_list[0].measurement_unit_code
                    qon.monetary_unit_code = qon.quota_definition_list[0].monetary_unit_code
                    qon.measurement_unit_qualifier_code = qon.quota_definition_list[0].measurement_unit_qualifier_code

                    # print(qon.quota_order_number_id, qon.validity_start_date, qon.validity_end_date)

                last_order_number = "00.0000"
                last_duty = "-1"

                for comm in qon.commodity_list:
                    # Run a check to ensure that there are no 10 digit codes being added to the extract
                    # where the 8 digit code is also being displayed, and the duties are the same
                    if comm.commodity_code[8:] != "00":
                        my_duty = comm.duty_string
                        for sub_commodity in qon.commodity_list:
                            if sub_commodity.commodity_code == comm.commodity_code[0:8] + "00":
                                if sub_commodity.duty_string == my_duty:
                                    comm.suppress = True

                    if comm.suppress is False:
                        insert_divider = False
                        insert_duty_divider = False
                        row_string = self.application.sQuotaTableRowXML
                        row_string = row_string.replace("{COMMODITY_CODE}", comm.commodity_code_formatted)
                        # row_string = row_string.replace("{COMMODITY_CODE}", comm.commodity_code)

                        if last_order_number == qon.quota_order_number_id:
                            row_string = row_string.replace("{QUOTA_ORDER_NUMBER}",		"")
                            row_string = row_string.replace("{ORIGIN_QUOTA}",   		"")
                            row_string = row_string.replace("{QUOTA_VOLUME}",			"")
                            row_string = row_string.replace("{QUOTA_OPEN_DATE}",		"")
                            row_string = row_string.replace("{QUOTA_CLOSE_DATE}",		"")
                            row_string = row_string.replace("{QUOTA_OPEN_DATE_2019}",	"")
                            row_string = row_string.replace("{QUOTA_CLOSE_DATE_2019}",	"")
                            row_string = row_string.replace("{2019_QUOTA_VOLUME}",		"")
                            # row_string = row_string.replace("<!--OPT//--><w:r><w:br/></w:r><!--OPT//-->",		"")
                            row_string = re.sub(
                                "<!-- Begin Quota Volume cell //-->.*<!-- End Quota Volume cell //-->",
                                '<!-- Begin Quota Volume cell //-->\n'
                                '<w:tc><w:tcPr><w:vMerge/></w:tcPr><w:p><w:pPr><w:pStyle w:val="NormalinTable"/>'
                                '</w:pPr><w:r><w:t></w:t></w:r></w:p></w:tc>\n<!-- End Quota Volume cell //-->',
                                row_string,
                                flags=re.DOTALL
                            )

                        else:
                            qon.format_order_number()

                            # Final fixes to the 2019 dates
                            # print(qon.quota_order_number_id, qon.validity_start_date_2019, qon.validity_end_date_2019,
                            # (qon.validity_end_date_2019 - qon.validity_start_date_2019).days)

                            if qon.suspended:
                                row_string = row_string.replace(
                                    "{QUOTA_ORDER_NUMBER}",	qon.quota_order_number_id_formatted + " (suspended)"
                                )
                            else:
                                row_string = row_string.replace(
                                    "{QUOTA_ORDER_NUMBER}",	qon.quota_order_number_id_formatted
                                )

                            row_string = row_string.replace(
                                "{ORIGIN_QUOTA}", qon.origin_quota
                            )
                            if qon.addendum != "":
                                row_string = row_string.replace(
                                    "{QUOTA_VOLUME}", qon.volume_yx + " + " + qon.addendum
                                )
                            else:
                                row_string = row_string.replace(
                                    "{QUOTA_VOLUME}", qon.volume_yx
                                )

                            row_string = row_string.replace(
                                "{QUOTA_OPEN_DATE}", datetime.strftime(qon.validity_start_date, '%d/%m')
                            )
                            row_string = row_string.replace(
                                "{QUOTA_CLOSE_DATE}", datetime.strftime(qon.validity_end_date, '%d/%m')
                            )

                            if qon.initial_volume[0] == "0":
                                row_string = row_string.replace("{2019_QUOTA_VOLUME}",		"")
                                row_string = row_string.replace("{QUOTA_OPEN_DATE_2019}",	"")
                                row_string = row_string.replace("{QUOTA_CLOSE_DATE_2019}",	"")
                                row_string = row_string.replace("<!--OPT//--><w:r><w:br/></w:r><!--OPT//-->",		"")
                                row_string = re.sub(
                                    "<!--19VStart//-->.*<!--19VEnd//-->", "", row_string, flags=re.DOTALL
                                )
                                row_string = re.sub(
                                    "<!--19VStartb//-->.*<!--19VEndb//-->", "", row_string, flags=re.DOTALL
                                )
                                row_string = re.sub(
                                    "<!--19VStartc//-->.*<!--19VEndc//-->", "", row_string, flags=re.DOTALL
                                )
                            else:
                                row_string = row_string.replace(
                                    "{2019_QUOTA_VOLUME}", str(qon.initial_volume).strip() + " (2019)"
                                )
                                row_string = row_string.replace(
                                    "{QUOTA_OPEN_DATE_2019}",
                                    datetime.strftime(qon.validity_start_date_2019, '%d/%m/%Y')
                                )
                                row_string = row_string.replace(
                                    "{QUOTA_CLOSE_DATE_2019}",
                                    datetime.strftime(qon.validity_end_date_2019, '%d/%m/%Y')
                                )

                            insert_divider = True

                        if comm.duty_string != last_duty:
                            row_string = row_string.replace("{PREFERENTIAL_DUTY_RATE}",	comm.duty_string)
                            insert_duty_divider = True
                        else:
                            row_string = row_string.replace("{PREFERENTIAL_DUTY_RATE}",	"")

                        row_string = row_string.replace("{PREFERENTIAL_DUTY_RATE}",	comm.duty_string)

                        if insert_divider:
                            row_string = row_string.replace("<w:tc>", "<w:tc>\n" + self.application.sHorizLineXML)
                        elif insert_duty_divider:
                            row_string = row_string.replace("<w:tc>", "<w:tc>\n" + self.application.sHorizLineSoftXML)
                            pass

                        if last_order_number == qon.quota_order_number_id:
                            # Test code - replace the Origin quota cell with a merged cell
                            row_string = re.sub("<!-- Begin quota number cell //-->.*<!-- End quota number cell //-->", '<!-- Begin quota number cell //-->\n<w:tc><w:tcPr><w:vMerge/></w:tcPr><w:p><w:pPr><w:pStyle w:val="NormalinTable"/></w:pPr><w:r><w:t></w:t></w:r></w:p></w:tc>\n<!-- End quota number cell //-->', row_string, flags=re.DOTALL)
                            row_string = re.sub("<!-- Begin origin quota cell //-->.*<!-- End origin quota cell //-->", '<!-- Begin origin quota cell //-->\n<w:tc><w:tcPr><w:vMerge/></w:tcPr><w:p><w:pPr><w:pStyle w:val="NormalinTable"/></w:pPr><w:r><w:t></w:t></w:r></w:p></w:tc>\n<!-- End origin quota cell //-->', row_string, flags=re.DOTALL)
                            row_string = re.sub("<!-- Begin Quota Volume cell //-->.*<!-- End Quota Volume cell //-->", '<!-- Begin Quota Volume cell //-->\n<w:tc><w:tcPr><w:vMerge/></w:tcPr><w:p><w:pPr><w:pStyle w:val="NormalinTable"/></w:pPr><w:r><w:t></w:t></w:r></w:p></w:tc>\n<!-- End Quota Volume cell //-->', row_string, flags=re.DOTALL)
                            row_string = re.sub("<!-- Begin Quota Open Date cell //-->.*<!-- End Quota Open Date cell //-->", '<!-- Begin Quota Open Date cell //-->\n<w:tc><w:tcPr><w:vMerge/></w:tcPr><w:p><w:pPr><w:pStyle w:val="NormalinTable"/></w:pPr><w:r><w:t></w:t></w:r></w:p></w:tc>\n<!-- End Quota Open Date cell //-->', row_string, flags=re.DOTALL)
                            row_string = re.sub("<!-- Begin Quota Close Date cell //-->.*<!-- End Quota Close Date cell //-->", '<!-- Begin Quota Close Date cell //-->\n<w:tc><w:tcPr><w:vMerge/></w:tcPr><w:p><w:pPr><w:pStyle w:val="NormalinTable"/></w:pPr><w:r><w:t></w:t></w:r></w:p></w:tc>\n<!-- End Quota Close Date cell //-->', row_string, flags=re.DOTALL)
                            row_string = re.sub("<!-- Begin Quota Close Date cell //-->.*<!-- End Quota Close Date cell //-->", '<!-- Begin Quota Close Date cell //-->\n<w:tc><w:tcPr><w:vMerge/></w:tcPr><w:p><w:pPr><w:pStyle w:val="NormalinTable"/></w:pPr><w:r><w:t></w:t></w:r></w:p></w:tc>\n<!-- End Quota Close Date cell //-->', row_string, flags=re.DOTALL)
                            pass

                        if last_duty == comm.duty_string:
                            row_string = re.sub("<!-- Begin Preferential Quota Duty Rate cell //-->.*<!-- End Preferential Quota Duty Rate cell //-->", '<!-- Begin Preferential Quota Duty Rate cell //-->\n<w:tc><w:tcPr><w:vMerge/></w:tcPr><w:p><w:pPr><w:pStyle w:val="NormalinTable"/></w:pPr><w:r><w:t></w:t></w:r></w:p></w:tc>\n<!-- End Preferential Quota Duty Rate cell //-->', row_string, flags=re.DOTALL)

                        last_order_number = qon.quota_order_number_id
                        last_duty = comm.duty_string

                        table_content += row_string

        ###########################################################################
        # Write the main document
        ###########################################################################

        quota_xml = ""
        sTableXML = self.application.sQuotaTableXML
        width_list = [8, 7, 11, 22, 16, 10, 10, 16]

        sTableXML = sTableXML.replace("{WIDTH_QUOTA_NUMBER}", str(width_list[0]))
        sTableXML = sTableXML.replace("{WIDTH_ORIGIN_QUOTA}", str(width_list[1]))
        sTableXML = sTableXML.replace("{WIDTH_COMMODITY_CODE}",	str(width_list[2]))
        sTableXML = sTableXML.replace("{WIDTH_PREFERENTIAL_QUOTA_DUTY_RATE}", str(width_list[3]))
        sTableXML = sTableXML.replace("{WIDTH_QUOTA_VOLUME}", str(width_list[4]))
        sTableXML = sTableXML.replace("{WIDTH_QUOTA_OPEN_DATE}", str(width_list[5]))
        sTableXML = sTableXML.replace("{WIDTH_QUOTA_CLOSE_DATE}", str(width_list[6]))
        sTableXML = sTableXML.replace("{WIDTH_2019_QUOTA_VOLUME}", str(width_list[7]))

        sTableXML = sTableXML.replace("{TABLEBODY}", table_content)

        quota_xml += sTableXML

        self.document_xml = self.document_xml.replace("{QUOTA TABLE GOES HERE}", quota_xml)


    def write(self):
        ###########################################################################
        # WRITE document.xml
        ###########################################################################
        FILENAME = os.path.join(self.application.WORD_DIR, "document.xml")

        file = codecs.open(FILENAME, "w", "utf-8")
        file.write(self.document_xml)
        file.close()

        ###########################################################################
        # Finally, ZIP everything up
        ###########################################################################
        self.FILENAME = self.application.country_profile + "_annex.docx"
        self.word_filename = os.path.join(self.application.OUTPUT_DIR, self.FILENAME)
        f.zipdir(self.word_filename)

    def print_tariffs(self):
        print(" - Getting preferential duties")

        # Run a check to ensure that there are no 10 digit codes being added to the extract
        # where the 8 digit code is also being displayed, and the duties are the same
        # I may need this again
        """
        for my_measure in measure_list:
            if my_measure.commodity_code[8:] != "00":
                my_duty = my_measure.combined_duty
                for sub_commodity in measure_list:
                    if sub_commodity.commodity_code == my_measure.commodity_code[0:8] + "00":
                        if sub_commodity.combined_duty == my_duty:
                            my_measure.suppress_row = True
        """

        ###########################################################################
        # Output the rows to buffer
        ###########################################################################

        table_content = ""
        for c in self.commodity_list:
            if c.suppress is False:
                row_string = self.application.sTableRowXML
                row_string = row_string.replace("{COMMODITY}", c.commodity_code_formatted)
                # row_string = row_string.replace("{COMMODITY}", c.commodity_code)
                if c.duty_string[-18:] == "<w:r><w:br/></w:r>":
                    c.duty_string = c.duty_string[:-18]
                row_string = row_string.replace("{DUTY}", c.duty_string)
                table_content += row_string

        ###########################################################################
        # Write the main document
        ###########################################################################

        tariff_xml = ""

        sTableXML = self.application.sTableXML
        width_list = [400, 1450, 1150, 2000]
        sTableXML = sTableXML.replace("{WIDTH_CLASSIFICATION}", str(width_list[0]))
        sTableXML = sTableXML.replace("{WIDTH_DUTY}", str(width_list[1]))
        sTableXML = sTableXML.replace("{TABLEBODY}", table_content)

        tariff_xml += sTableXML
        self.document_xml = self.application.sDocumentXML
        self.document_xml = self.document_xml.replace("{TARIFF TABLE GOES HERE}", tariff_xml)
