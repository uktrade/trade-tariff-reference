import json
import os
import os.path
from datetime import datetime

import trade_tariff_reference.documents.fta.functions as f
from trade_tariff_reference.documents.fta.constants import (
    GET_COMMODITIES_SQL,
    GET_MEUSRING_COMPONENTS_DUTY_AVERAGE_SQL,
    GET_MEUSRING_PERCENTAGE_SQL,
    GET_MFNS_FOR_SIV_PRODUCTS_SQL,
)
from trade_tariff_reference.documents.fta.database import DatabaseConnect
from trade_tariff_reference.documents.fta.document import Document
from trade_tariff_reference.documents.fta.exceptions import CountryProfileError
from trade_tariff_reference.documents.fta.local_siv import LocalSiv
from trade_tariff_reference.documents.fta.mfn_duty import MfnDuty


class Application(DatabaseConnect):

    def __init__(self, country_profile):
        self.country_profile = country_profile
        self.debug = False
        self.country_codes = ""

        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.CSV_DIR = os.path.join(self.BASE_DIR, "csv")
        self.COMPONENT_DIR = os.path.join(self.BASE_DIR, "../templates/xml")

        # For the output folders
        self.OUTPUT_DIR = os.path.join(self.BASE_DIR, "output")
        self._get_config()
        self.connect()

        # MPP TODO: Move these
        self.erga_omnes_average = None
        self.mfn_list = []
        self.all_country_profiles = {}
        self.exclusion_check = ""

    def _get_config(self,):
        self.get_config()

        # Unless we are running a sequence, find the country code

        self.get_country_list()
        self.geo_ids = f.list_to_sql(self.country_codes)

    def get_commodities_for_local_sivs(self):
        # Get commodities where there is a local SIV
        rows = self.execute_sql(
            GET_COMMODITIES_SQL.format(geo_ids=self.geo_ids)
        )

        self.local_sivs = []
        self.local_sivs_commodities_only = []

        for rw in rows:
            goods_nomenclature_item_id = rw[0]
            validity_start_date = rw[1]
            condition_duty_amount = rw[2]
            condition_monetary_unit_code = rw[3]
            condition_measurement_unit_code = rw[4]

            obj = LocalSiv(
                goods_nomenclature_item_id,
                validity_start_date,
                condition_duty_amount,
                condition_monetary_unit_code,
                condition_measurement_unit_code,
            )
            self.local_sivs.append(obj)
            self.local_sivs_commodities_only.append(goods_nomenclature_item_id)

    def create_document(self):
        # Create the document
        my_document = Document(self)
        self.get_meursing_components()

        # Get commodities where there is a local SIV
        self.get_commodities_for_local_sivs()

        # Create the measures table
        my_document.get_duties("preferences")
        tariff_data = my_document.print_tariffs()

        # Create the quotas table
        my_document.get_duties("quotas")
        my_document.get_quota_order_numbers()
        my_document.get_quota_balances_from_csv()
        my_document.get_quota_measures()
        my_document.get_quota_definitions()
        quota_data = my_document.print_quotas()

        context_data = {
            'AGREEMENT_NAME': self.agreement_name,
            'VERSION': self.version,
            'AGREEMENT_DATE': self.agreement_date_long,
            'AGREEMENT_DATE_SHORT': self.agreement_date_short,
            'COUNTRY_NAME': self.country_name,
            **tariff_data,
            **quota_data,
        }

        # Personalise and write the document
        my_document.create_document(context_data)

    def get_config(self):
        config_dir = os.path.join(self.BASE_DIR, "config")
        config_file = os.path.join(config_dir, "config_common.json")
        config_file_local = os.path.join(
            config_dir,
            "config_migrate_measures_and_quotas.json",
        )
        # Get global config items
        with open(config_file, 'r') as f:
            my_dict = json.load(f)

        # Get local config items
        with open(config_file_local, 'r') as f:
            my_dict = json.load(f)

        self.all_country_profiles = my_dict['country_profiles']

    def get_country_list(self):
        try:
            profile = self.all_country_profiles[self.country_profile]
        except KeyError:
            raise CountryProfileError("Country profile does not exist")

        try:
            self.country_codes = profile['country_codes']
        except KeyError:
            raise CountryProfileError("Country profile has no country codes")

        # Get exclusions
        self.exclusion_check = profile.get("exclusion_check", "")

        # Get agreement name
        self.agreement_name = profile["agreement_name"]

        self.agreement_date_short = profile["agreement_date"]
        temp = datetime.strptime(self.agreement_date_short, "%d/%m/%Y")
        self.agreement_date_long = datetime.strftime(temp, "%d %B %Y").lstrip("0")

        self.table_per_country = profile["table_per_country"]
        self.version = profile["version"]
        self.country_name = profile["country_name"]

    def get_mfns_for_siv_products(self):
        f.log(" - Getting MFNs for SIV products")
        rows = self.execute_sql(GET_MFNS_FOR_SIV_PRODUCTS_SQL)
        for r in rows:
            f.log(r)
            goods_nomenclature_item_id = r[0]
            duty_amount = r[1]
            validity_start_date = r[2]
            validity_end_date = r[3]
            mfn = MfnDuty(
                goods_nomenclature_item_id,
                duty_amount,
                validity_start_date,
                validity_end_date
            )
            self.mfn_list.append(mfn)

    def get_mfn_rate(self, commodity_code, validity_start_date):
        mfn_rate = 0.0
        found = False
        for mfn in self.mfn_list:
            if commodity_code == mfn.commodity_code:
                if validity_start_date == mfn.validity_start_date:
                    mfn_rate = mfn.duty_amount
                    found = True
                    break
        if found is False:
            if commodity_code[8:10] != "00":
                commodity_code = commodity_code[0:8] + "00"
                mfn_rate = self.get_mfn_rate(
                    commodity_code,
                    validity_start_date,
                )
            elif commodity_code[6:10] != "0000":
                commodity_code = commodity_code[0:6] + "00"
                mfn_rate = self.get_mfn_rate(
                    commodity_code,
                    validity_start_date,
                )
        return mfn_rate

    def get_meursing_components(self):
        self.erga_omnes_average = self.execute_sql(GET_MEUSRING_COMPONENTS_DUTY_AVERAGE_SQL, only_one_row=True)[0]

    def get_meursing_percentage(self, reduction_indicator, geographical_area_id):
        # Get the Erga Omnes Meursing average
        reduced_average = self.execute_sql(
            GET_MEUSRING_PERCENTAGE_SQL.format(
                geographical_area_id=geographical_area_id,
                reduction_indicator=reduction_indicator
            ),
            only_one_row=True
        )[0]
        try:
            reduction = round((reduced_average / self.erga_omnes_average) * 100)
        except TypeError:
            reduction = 100
        return reduction
