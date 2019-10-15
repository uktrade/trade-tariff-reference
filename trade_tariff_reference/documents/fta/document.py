import codecs
import logging
import os
import tempfile
from datetime import datetime
from distutils.dir_util import copy_tree
from functools import lru_cache

from botocore.exceptions import EndpointConnectionError

from django.template.loader import render_to_string


import trade_tariff_reference.documents.functions as f
from trade_tariff_reference.documents.fta.commodity import Commodity
from trade_tariff_reference.documents.fta.constants import (
    CHECK_FOR_QUOTAS_SQL,
    FIRST_COME_FIRST_SERVED,
    GET_COMMODITIES_SQL,
    GET_DUTIES_SQL,
    GET_MEASURE_COMPONENTS_SQL,
    GET_QUOTA_BALANCE_SQL,
    GET_QUOTA_DEFINITIONS_SQL,
    GET_QUOTA_MEASURES_SQL,
    GET_QUOTA_ORDER_NUMBERS_SQL,
)
from trade_tariff_reference.documents.fta.duty import Duty
from trade_tariff_reference.documents.fta.local_siv import LocalSiv
from trade_tariff_reference.documents.fta.measure import Measure
from trade_tariff_reference.documents.fta.measure_condition import MeasureCondition
from trade_tariff_reference.documents.fta.quota_balance import QuotaBalance
from trade_tariff_reference.documents.fta.quota_commodity import QuotaCommodity
from trade_tariff_reference.documents.fta.quota_definition import QuotaDefinition
from trade_tariff_reference.documents.fta.quota_order_number import QuotaOrderNumber
from trade_tariff_reference.documents.history import AgreementDocumentHistoryLog
from trade_tariff_reference.documents.utils import upload_document_to_s3
from trade_tariff_reference.schedule.models import ExtendedQuota


logger = logging.getLogger(__name__)


class Document:

    def __init__(self, application):
        self.application = application
        self.footnote_list = []
        self.duty_list = []
        self.balance_dict = {}
        self.supplementary_unit_list = []
        self.quota_definition_list = []
        self.q = []
        self.quota_order_number_list = []
        self.seasonal_records = 0
        self.wide_duty = False
        self.has_quotas = False

        logger.debug("Creating FTA document for " + application.agreement.country_name + "\n")
        self.application.get_mfns_for_siv_products()

    def check_for_quotas(self):
        rows = self.application.execute_sql(
            CHECK_FOR_QUOTAS_SQL.format(geo_ids=self.application.agreement.geo_ids)
        )
        if len(rows) == 0:
            logger.debug(" - This FTA has no quotas")
            result = False
        else:
            logger.debug(" - This FTA has quotas")
            result = True
        self.has_quotas = result
        return result

    def get_measure_type_list_for_instrument_type(self, instrument_type):
        if instrument_type == "preferences":
            return "'142', '145'"
        return "'143', '146'"

    def get_measure_conditions(self, measure_type_list):
        measure_condition_dict = {}

        rows = self.application.execute_sql(
            GET_MEASURE_COMPONENTS_SQL.format(
                measure_type_list=measure_type_list,
                geo_ids=self.application.agreement.geo_ids,
            ),
            dict_cursor=True
        )
        for row in rows:
            mc = MeasureCondition(0, row['measure_sid'], "V", 1, row['duty_amount'], "", "", "", "", "", "")
            measure_condition_dict[row['measure_sid']] = mc
        return measure_condition_dict

    @lru_cache(maxsize=5)
    def get_commodities_for_local_sivs(self):
        # Get commodities where there is a local SIV
        rows = self.application.execute_sql(
            GET_COMMODITIES_SQL.format(geo_ids=self.application.agreement.geo_ids),
            dict_cursor=True
        )

        local_sivs = []
        local_sivs_commodities_only = []

        for row in rows:
            obj = LocalSiv(
                row['goods_nomenclature_item_id'],
                row['validity_start_date'],
                row['condition_duty_amount'],
                row['condition_monetary_unit_code'],
                row['condition_measurement_unit_code'],
            )
            local_sivs.append(obj)
            local_sivs_commodities_only.append(row['goods_nomenclature_item_id'])
        return local_sivs, local_sivs_commodities_only

    def _get_duties(self, measure_type_list):
        return self.application.execute_sql(
            GET_DUTIES_SQL.format(measure_type_list=measure_type_list, geo_ids=self.application.agreement.geo_ids),
            dict_cursor=True
        )

    def populate_duty_list(
        self,
        commodity_code,
        additional_code_type_id,
        additional_code_id,
        measure_type_id,
        duty_expression_id,
        duty_amount,
        monetary_unit_code,
        measurement_unit_code,
        measurement_unit_qualifier_code,
        measure_sid,
        quota_order_number_id,
        geographical_area_id,
        validity_start_date,
        validity_end_date,
        reduction_indicator,
        local_sivs,
        local_sivs_commodities_only,
        measure_condition_dict,
    ):
        if duty_amount is None and duty_expression_id is None:
            is_siv = True
            measure_condition = measure_condition_dict.get(measure_sid)
            if measure_condition:
                duty_expression_id = "01"
                duty_amount = measure_condition.condition_duty_amount
        else:
            is_siv = False

        obj_duty = Duty(
            self.application,
            commodity_code,
            additional_code_type_id,
            additional_code_id,
            measure_type_id,
            duty_expression_id,
            duty_amount,
            monetary_unit_code,
            measurement_unit_code,
            measurement_unit_qualifier_code,
            measure_sid,
            quota_order_number_id,
            geographical_area_id,
            validity_start_date,
            validity_end_date,
            reduction_indicator,
            is_siv,
            local_sivs,
            local_sivs_commodities_only
        )
        self.duty_list.append(obj_duty)

    def populate_measure_list(
        self,
        temp_measure_list,
        measure_sid,
        commodity_code,
        quota_order_number_id,
        validity_start_date,
        validity_end_date,
        geographical_area_id,
        reduction_indicator,
    ):
        if measure_sid not in temp_measure_list:
            obj_measure = Measure(
                measure_sid,
                commodity_code,
                quota_order_number_id,
                validity_start_date,
                validity_end_date,
                geographical_area_id,
                reduction_indicator
            )
            self.measure_list.append(obj_measure)
            temp_measure_list.append(measure_sid)

    def populate_commodity_list(
        self,
        temp_commodity_list,
        commodity_code,
    ):
        if commodity_code not in temp_commodity_list:
            obj_commodity = Commodity(commodity_code)
            self.commodity_list.append(obj_commodity)
            temp_commodity_list.append(commodity_code)

    def populate_quota_order_number_list(
        self,
        temp_quota_order_number_list,
        quota_order_number_id,
    ):
        if quota_order_number_id not in temp_quota_order_number_list:
            if quota_order_number_id != "":
                obj_quota_order_number = QuotaOrderNumber(quota_order_number_id)
                self.quota_order_number_list.append(obj_quota_order_number)
                temp_quota_order_number_list.append(quota_order_number_id)

    def get_duties(self, instrument_type):
        logger.debug(" - Getting duties for " + instrument_type)

        ###############################################################
        # Work out which measures to capture
        measure_type_list = self.get_measure_type_list_for_instrument_type(instrument_type)

        ###############################################################
        # Before getting the duties, get the measure component conditions
        # These are used in adding in SIV components whenever the duty is no present
        # due to the fact that there are SIVs applied via measure components
        logger.debug(" - Getting measure conditions")
        measure_condition_dict = self.get_measure_conditions(measure_type_list)

        # Get the duties (i.e the measure components)
        # Add this back in for Switzerland ( OR m.measure_sid = 3231905)
        duties = self._get_duties(measure_type_list)

        local_sivs, local_sivs_commodities_only = self.get_commodities_for_local_sivs()

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
            measure_sid = row['measure_sid']
            commodity_code = f.mstr(row['goods_nomenclature_item_id'])
            additional_code_type_id = f.mstr(row['additional_code_type_id'])
            additional_code_id = f.mstr(row['additional_code_id'])
            measure_type_id = f.mstr(row['measure_type_id'])
            duty_expression_id = row['duty_expression_id']
            duty_amount = row['duty_amount']
            monetary_unit_code = f.mstr(row['monetary_unit_code'])
            monetary_unit_code = monetary_unit_code.replace("EUR", "€")
            measurement_unit_code = f.mstr(row['measurement_unit_code'])
            measurement_unit_qualifier_code = f.mstr(row['measurement_unit_qualifier_code'])
            quota_order_number_id = f.mstr(row['ordernumber'])
            validity_start_date = row['validity_start_date']
            validity_end_date = row['validity_end_date']
            geographical_area_id = f.mstr(row['geographical_area_id'])
            reduction_indicator = row['reduction_indicator']

            # Hypothesis would be that the only reason why the Duty amount is None is when
            # there is a "V" code attached to the Measure
            # if ((duty_amount is None) and (duty_expression_id == "01")):
            self.populate_duty_list(
                commodity_code,
                additional_code_type_id,
                additional_code_id,
                measure_type_id,
                duty_expression_id,
                duty_amount,
                monetary_unit_code,
                measurement_unit_code,
                measurement_unit_qualifier_code,
                measure_sid,
                quota_order_number_id,
                geographical_area_id,
                validity_start_date,
                validity_end_date,
                reduction_indicator,
                local_sivs,
                local_sivs_commodities_only,
                measure_condition_dict,
            )

            self.populate_measure_list(
                temp_measure_list,
                measure_sid,
                commodity_code,
                quota_order_number_id,
                validity_start_date,
                validity_end_date,
                geographical_area_id,
                reduction_indicator,
            )

            self.populate_commodity_list(
                temp_commodity_list,
                commodity_code
            )

            self.populate_quota_order_number_list(
                temp_quota_order_number_list,
                quota_order_number_id
            )

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
        logger.debug(" - Getting unique quota order numbers")
        # Get unique order numbers

        rows = self.application.execute_sql(
            GET_QUOTA_ORDER_NUMBERS_SQL.format(geo_ids=self.application.agreement.geo_ids),
        )
        if len(rows) == 0:
            self.has_quotas = False
            return
        else:
            self.has_quotas = True

        for row in rows:
            quota_order_number_id = row[0]
            qon = QuotaOrderNumber(quota_order_number_id)
            self.quota_order_number_list.append(qon)
            self.q.append(quota_order_number_id)

    def get_measure_list(self):
        measure_list = []
        rows = self.application.execute_sql(
            GET_QUOTA_MEASURES_SQL.format(geo_ids=self.application.agreement.geo_ids),
            dict_cursor=True
        )

        for row in rows:
            measure = Measure(
                row['measure_sid'],
                row['goods_nomenclature_item_id'],
                row['ordernumber'],
                row['validity_start_date'],
                row['validity_end_date'],
                row['geographical_area_id'],
                row['reduction_indicator']
            )
            measure_list.append(measure)
        return measure_list

    def get_quota_measures(self):
        # print(len(self.commodity_list))
        # Get the measures - in order to get the commodity codes and the duties
        # Just get the commodities and add to an array
        self.measure_list = self.get_measure_list()
        if not self.measure_list:
            self.has_quotas = False
            return

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

    def get_quota_balances(self):
        if self.has_quotas is False:
            return
        self.add_first_come_first_serve_quotas()
        self.add_licensed_quotas()

    def add_licensed_quotas(self):
        temp = ExtendedQuota.objects.filter(
            agreement=self.application.agreement,
            quota_type=ExtendedQuota.LICENSED
        )
        for balance in temp:
            quota_order_number_id = balance.quota_order_number_id
            country = balance.agreement.slug
            method = balance.get_quota_type_display()
            y1_balance = balance.year_start_balance
            yx_balance = balance.opening_balance
            yx_start = balance.start_date
            measurement_unit_code = balance.measurement_unit_code
            origin_quota = "Y" if balance.is_origin_quota else ""
            addendum = balance.addendum
            scope = balance.scope
            qb = QuotaBalance(
                quota_order_number_id,
                country,
                method,
                y1_balance,
                yx_balance,
                yx_start,
                measurement_unit_code,
                origin_quota,
                addendum,
                scope
            )
            if str(quota_order_number_id) not in self.balance_dict:
                self.balance_dict[str(quota_order_number_id)] = qb

    def add_first_come_first_serve_quotas(self):
        temp = self.application.execute_sql(
            GET_QUOTA_BALANCE_SQL.format(geo_ids=self.application.agreement.geo_ids),
            dict_cursor=True
        )
        for balance in temp:
            quota_order_number_id = balance['quota_order_number_id']
            extended_quota_info = self.get_extended_quota_information(quota_order_number_id)
            if not extended_quota_info:
                origin_quota = ""
                addendum = ""
                scope = ""
            else:
                addendum = extended_quota_info.addendum
                scope = extended_quota_info.scope
                origin_quota = "Y" if extended_quota_info.is_origin_quota else ""

            country = self.application.agreement.slug
            y1_balance = balance['initial_volume']
            yx_balance = balance['volume']
            yx_start = balance['validity_start_date']
            measurement_unit_code = balance['measurement_unit_code']

            qb = QuotaBalance(
                quota_order_number_id,
                country,
                FIRST_COME_FIRST_SERVED,
                y1_balance,
                yx_balance,
                yx_start,
                measurement_unit_code,
                origin_quota,
                addendum,
                scope
            )
            if str(quota_order_number_id) not in self.balance_dict:
                self.balance_dict[str(quota_order_number_id)] = qb

    def get_extended_quota_information(self, quota_order_number_id):
        return ExtendedQuota.objects.filter(
            quota_order_number_id=quota_order_number_id,
            agreement=self.application.agreement
        ).first()

    def get_quota_definitions(self):
        if self.has_quotas is False:
            return

        # Now get the quota definitions - this just gets quota definitions for FCFS quota
        # Any licensed quotas with first three characters "094" needs there to be an additional step to get the balances
        # as per function "get_quota_balances" above

        my_order_numbers = f.list_to_sql(self.q)

        rows = self.application.execute_sql(
            GET_QUOTA_DEFINITIONS_SQL.format(order_numbers=my_order_numbers),
            dict_cursor=True
        )

        self.quota_definition_list = []
        for row in rows:
            qd = QuotaDefinition(
                row['quota_definition_sid'],
                row['quota_order_number_id'],
                row['validity_start_date'],
                row['validity_end_date'],
                row['quota_order_number_sid'],
                row['volume'],
                row['initial_volume'],
                row['measurement_unit_code'],
                row['maximum_precision'],
                row['critical_state'],
                row['critical_threshold'],
                row['monetary_unit_code'],
                row['measurement_unit_qualifier_code'],
            )

            qb = self.balance_dict.get(str(qd.quota_order_number_id))
            if qb:
                qd.initial_volume = f.mnum(qb.y1_balance)
                qd.volume_yx = f.mnum(qb.yx_balance)
                qd.addendum = qb.addendum
                qd.scope = qb.scope
                qd.format_volumes()
            else:
                logger.critical(f"Matching balance not found {qd.quota_order_number_id}")
            qd.format_volumes()
            self.quota_definition_list.append(qd)

        # This process goes through the balance list (derived from the CSV) and assigns both the 2020 balance to the
        # quota definition object, as well as assigning the 2019 and 2020 balance to the licensed quotas
        # Stop press: I need to also assign the 2019 balance from the CSV, as this is a process run entirely against
        # the EU's files, not the UK's
        for qon in self.quota_order_number_list:
            qb = self.balance_dict.get(str(qon.quota_order_number_id))
            if qon.quota_order_number_id[0:3] == "094" and qb:
                # For licensed quotas, we need to create a brand new (artifical, not DB-persisted)
                # definition, for use in the creation of the FTA document only
                if qb.measurement_unit_code == "":
                    qb.measurement_unit_code = "KGM"
                d1 = qb.yx_start
                d2 = qb.yx_end
                qd = QuotaDefinition(
                    0,
                    qon.quota_order_number_id,
                    d1,
                    d2,
                    0,
                    int(qb.y1_balance),
                    int(qb.y1_balance),
                    qb.measurement_unit_code,
                    3,
                    "Y",
                    90,
                    "",
                    ""
                )
                qd.volume_yx = int(qb.yx_balance)
                qd.addendum = qb.addendum.strip()
                qd.scope = qb.scope.strip()
                qd.format_volumes()
                self.quota_definition_list.append(qd)
            if qb:
                # Now get the quota origins from the balance file
                # Now get the 2019 start date from the balance file
                qon.origin_quota = qb.origin_quota
                qon.validity_start_date_2019 = qb.validity_start_date_2019

        # Finally, add the quota definitions, replete with their new balances
        # to the relevant quota order numbers

        d = {}
        for q in self.quota_definition_list:
            d[q.quota_order_number_id] = q

        for qon in self.quota_order_number_list:
            if qon.quota_order_number_id in d:
                qon.quota_definition_list.append(d[qon.quota_order_number_id])

    def get_quota_start_date(self, start_date):
        if not start_date:
            return ""
        return datetime.strftime(start_date, '%d/%m')

    def get_quota_end_date(self, end_date):
        if not end_date:
            return ""
        return datetime.strftime(end_date, '%d/%m')

    def print_quotas(self):
        logger.debug(" - Getting quotas")
        quota_list = []

        self.quota_order_number_list.sort(key=lambda x: x.quota_order_number_id, reverse=False)
        for qon in self.quota_order_number_list:

            # Check balance info has been provided, if not then do not display
            qb = self.balance_dict.get(str(qon.quota_order_number_id))

            if qb:
                # TODO: MPP what should the dates be for licensed quotas
                qon.validity_start_date = qon.quota_definition_list[0].validity_start_date
                qon.validity_end_date = qon.quota_definition_list[0].validity_end_date
                qon.validity_end_date_2019 = qon.quota_definition_list[0].validity_end_date
                qon.validity_start_date_2019 = qon.quota_definition_list[0].validity_start_date

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
                    table_row = {}
                    if comm.suppress is False:

                        if last_order_number == qon.quota_order_number_id:
                            table_row = {
                                'QUOTA_ORDER_NUMBER': '',
                                'ORIGIN_QUOTA': '',
                                'QUOTA_VOLUME': '',
                                'QUOTA_OPEN_DATE': '',
                                'QUOTA_CLOSE_DATE': '',
                                '2019_QUOTA_VOLUME': '',
                                'QUOTA_OPEN_DATE_2019': '',
                                'QUOTA_CLOSE_DATE_2019': '',
                                'INSERT_DIVIDER': False,
                                'EMPTY_QUOTA_VOLUME_CELL': True,
                            }

                        else:
                            qon.format_order_number()

                            # Final fixes to the 2019 dates
                            # print(qon.quota_order_number_id, qon.validity_start_date_2019, qon.validity_end_date_2019,
                            # (qon.validity_end_date_2019 - qon.validity_start_date_2019).days)

                            quota_order_number = qon.quota_order_number_id_formatted
                            if qon.suspended:
                                quota_order_number = f'{quota_order_number} (suspended)'

                            quota_volume = qon.volume_yx
                            if qon.addendum != "":
                                quota_volume = f'{quota_volume} + {qon.addendum}'

                            table_row = {
                                'QUOTA_ORDER_NUMBER': quota_order_number,
                                'ORIGIN_QUOTA': qon.origin_quota,
                                'QUOTA_VOLUME': quota_volume,
                                'QUOTA_OPEN_DATE': self.get_quota_start_date(qon.validity_start_date),
                                'QUOTA_CLOSE_DATE': self.get_quota_end_date(qon.validity_end_date),
                                '2019_QUOTA_VOLUME': '',
                                'QUOTA_OPEN_DATE_2019': '',
                                'QUOTA_CLOSE_DATE_2019': '',
                                'INSERT_DIVIDER': True
                            }

                            if not qon.initial_volume.startswith("0"):
                                table_row['2019_QUOTA_VOLUME'] = f'{str(qon.initial_volume).strip()} (2019)'
                                table_row['QUOTA_OPEN_DATE_2019'] = datetime.strftime(
                                    qon.validity_start_date_2019, '%d/%m/%Y'
                                )
                                table_row['QUOTA_CLOSE_DATE_2019'] = datetime.strftime(
                                    qon.validity_end_date_2019, '%d/%m/%Y'
                                )

                        table_row['COMMODITY_CODE'] = comm.commodity_code_formatted
                        table_row['PREFERENTIAL_DUTY_RATE'] = comm.duty_string

                        if comm.duty_string != last_duty:
                            table_row['INSERT_DUTY_DIVIDER'] = True

                        if last_order_number == qon.quota_order_number_id:
                            table_row.update(
                                {
                                    'EMPTY_QUOTA_ORDER_NUMBER_CELL': True,
                                    'EMPTY_ORIGIN_QUOTA_CELL': True,
                                    'EMPTY_QUOTA_VOLUME_CELL': True,
                                    'EMPTY_QUOTA_OPEN_DATE_CELL': True,
                                    'EMPTY_QUOTA_CLOSE_DATE_CELL': True,
                                }
                            )

                        if last_duty == comm.duty_string:
                            table_row['EMPTY_PREFERENTIAL_DUTY_RATE_CELL'] = True
                        last_order_number = qon.quota_order_number_id
                        last_duty = comm.duty_string
                    quota_list.append(table_row)

        quota_data = {
            'WIDTH_QUOTA_NUMBER': '8',
            'WIDTH_ORIGIN_QUOTA': '7',
            'WIDTH_COMMODITY_CODE': '11',
            'WIDTH_PREFERENTIAL_QUOTA_DUTY_RATE': '22',
            'WIDTH_QUOTA_VOLUME': '16',
            'WIDTH_QUOTA_OPEN_DATE': '10',
            'WIDTH_QUOTA_CLOSE_DATE': '10',
            'WIDTH_2019_QUOTA_VOLUME': '16',
            'QUOTA_TABLE_ROWS': quota_list,
            'HAS_QUOTAS': self.has_quotas,
        }
        return quota_data

    def get_document_xml(self, context):
        document_template = "xml/fta/document_noquotas.xml"
        if context.get('HAS_QUOTAS'):
            document_template = "xml/fta/document_hasquotas.xml"
        return render_to_string(document_template, context)

    def create_document(self, context):
        agreement_log = AgreementDocumentHistoryLog(
            self.application.agreement,
            context,
            self.application.force_document_generation
        )
        if agreement_log.change == dict() and not self.application.force_document_generation:
            logger.info(
                f'PROCESS COMPLETE - Document for {self.application.agreement.slug} unchanged no file generated')
            return

        document_xml = self.get_document_xml(context)
        try:
            remote_file_name = self.write(document_xml)
        except EndpointConnectionError:
            logger.error(
                f'Error - Cannot connect to S3 unable to update document for {self.application.agreement.slug}'
            )
        else:
            agreement_log.log_document_history(remote_file_name)

    def write(self, document_xml):
        ###########################################################################
        # WRITE document.xml
        ###########################################################################
        model_dir = os.path.join(self.application.BASE_DIR, 'model')
        docx_file_name = self.application.agreement.slug + "_annex.docx"

        with tempfile.TemporaryDirectory(prefix='document_generation') as tmp_model_dir:
            copy_tree(model_dir, tmp_model_dir)

            tmp_word_dir = os.path.join(tmp_model_dir, "word")

            file_name = os.path.join(tmp_word_dir, "document.xml")
            file = codecs.open(file_name, "w", "utf-8")
            file.write(document_xml)
            file.close()

            ###########################################################################
            # Finally, ZIP everything up
            ###########################################################################
            temp_doc_file = tempfile.NamedTemporaryFile()
            f.zipdir(tmp_model_dir, temp_doc_file.name)
            remote_file_name = upload_document_to_s3(self.application.agreement, temp_doc_file.name)
            logger.info(f"PROCESS COMPLETE - {docx_file_name} created - remote name {remote_file_name}")
            return remote_file_name

    def print_tariffs(self):
        logger.debug(" - Getting preferential duties")
        table_rows = []
        for c in self.commodity_list:
            if c.suppress is False:
                table_dict = {
                    'COMMODITY': c.commodity_code_formatted,
                }
                if c.duty_string[-18:] == "<w:r><w:br/></w:r>":
                    c.duty_string = c.duty_string[:-18]
                table_dict['DUTY'] = c.duty_string
                table_rows.append(table_dict)

        ###########################################################################
        # Write the main document
        ###########################################################################

        return {
            'TARIFF_WIDTH_CLASSIFICATION': '400',
            'TARIFF_WIDTH_DUTY': '1450',
            'TARIFF_TABLE_ROWS': table_rows,
        }
