import os
import os.path

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
from trade_tariff_reference.schedule.models import Agreement


class Application(DatabaseConnect):

    def __init__(self, country_profile):
        self.agreement = self.get_agreement(country_profile)

        self.debug = False

        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.COMPONENT_DIR = os.path.join(self.BASE_DIR, "../templates/xml")

        # For the output folders
        self.OUTPUT_DIR = os.path.join(self.BASE_DIR, "output")
        self.connect()

        # MPP TODO: Move these
        self.mfn_list = []

    def get_agreement(self, country_profile):
        try:
            profile = Agreement.objects.get(slug=country_profile)
        except Agreement.DoesNotExist:
            raise CountryProfileError('Country profile does not exist')
        if not profile.country_codes:
            raise CountryProfileError('Country profile has no country codes')
        return profile

    def get_commodities_for_local_sivs(self):
        # Get commodities where there is a local SIV
        rows = self.execute_sql(
            GET_COMMODITIES_SQL.format(geo_ids=self.agreement.geo_ids)
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
            'AGREEMENT_NAME': self.agreement.agreement_name,
            'VERSION': self.agreement.version,
            'AGREEMENT_DATE': self.agreement.agreement_date_long,
            'AGREEMENT_DATE_SHORT': self.agreement.agreement_date_short,
            'COUNTRY_NAME': self.agreement.country_name,
            **tariff_data,
            **quota_data,
        }

        # Personalise and write the document
        my_document.create_document(context_data)

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
        return self.execute_sql(GET_MEUSRING_COMPONENTS_DUTY_AVERAGE_SQL, only_one_row=True)[0]

    def get_meursing_percentage(self, reduction_indicator, geographical_area_id):
        erga_omnes_average = self.get_meursing_components()
        # Get the Erga Omnes Meursing average
        reduced_average = self.execute_sql(
            GET_MEUSRING_PERCENTAGE_SQL.format(
                geographical_area_id=geographical_area_id,
                reduction_indicator=reduction_indicator
            ),
            only_one_row=True
        )[0]
        try:
            reduction = round((reduced_average / erga_omnes_average) * 100)
        except TypeError:
            reduction = 100
        return reduction
