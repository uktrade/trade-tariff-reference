import sys
import os
import os.path
import json

from datetime import datetime

import documents.fta.functions as f
from documents.fta.constants import *
from documents.fta.database import DatabaseConnect
from documents.fta.document import Document
from documents.fta.mfn_duty import MfnDuty
from documents.fta.local_siv import LocalSiv


class Application(DatabaseConnect):

    def __init__(self, country_profile):
        self.country_profile = country_profile
        self.siv_list = []
        self.meursing_list = []
        self.vessels_list = []
        self.civilair_list = []
        self.airworthiness_list = []
        self.aircraft_list = []
        self.pharmaceuticals_list = []
        self.ita_list = []
        self.generalrelief_list = []
        self.authoriseduse_list = []
        self.seasonal_list = []
        self.special_list = []
        self.section_chapter_list = []
        self.lstFootnotes = []
        self.lstFootnotesUnique = []
        self.debug = False
        self.suppress_duties = False
        self.country_codes = ""
        self.siv_data_list = []
        self.seasonal_fta_duties = []
        self.meursing_components = []

        self.partial_temporary_stops = []

        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.SOURCE_DIR = os.path.join(self.BASE_DIR, "source")
        self.CSV_DIR = os.path.join(self.BASE_DIR, "csv")
        self.COMPONENT_DIR = os.path.join(self.BASE_DIR, "xmlcomponents")

        self.CONFIG_DIR = os.path.join(self.BASE_DIR, "config")
        self.CONFIG_FILE = os.path.join(self.CONFIG_DIR, "config_common.json")
        self.CONFIG_FILE_LOCAL = os.path.join(
            self.CONFIG_DIR,
            "config_migrate_measures_and_quotas.json",
        )
        self.BALANCE_FILE = os.path.join(self.CONFIG_DIR, "quota_volume_master.csv")
        self.MODEL_DIR = os.path.join(self.BASE_DIR, "model")
        self.WORD_DIR = os.path.join(self.MODEL_DIR, "word")
        self.DOCPROPS_DIR = os.path.join(self.MODEL_DIR, "docProps")

        # For the output folders
        self.OUTPUT_DIR = os.path.join(self.BASE_DIR, "output")
        self._get_config()
        self.connect()

        # MPP TODO: Move these
        self.erga_omnes_average = None
        self.mfn_list = []

    def _get_config(self):
        self.get_config()

        # Unless we are running a sequence, find the country code

        self.get_country_list()
        self.geo_ids = f.list_to_sql(self.country_codes)

    def create_document(self):
        # Create the document
        my_document = Document(self)
        self.get_meursing_components()
        my_document.check_for_quotas()
        self.readTemplates(my_document.has_quotas)

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

        # Create the measures table
        my_document.get_duties("preferences")
        my_document.print_tariffs()

        # Create the quotas table
        my_document.get_duties("quotas")
        my_document.get_quota_order_numbers()
        my_document.get_quota_balances_from_csv()
        my_document.get_quota_measures()
        my_document.get_quota_definitions()
        my_document.print_quotas()

        # Personalise and write the document
        my_document.create_core()
        my_document.write()
        print("\nPROCESS COMPLETE - file written to " + my_document.FILENAME + "\n")

    def get_config(self):
        # Get global config items
        with open(self.CONFIG_FILE, 'r') as f:
            my_dict = json.load(f)

        # Get local config items
        with open(self.CONFIG_FILE_LOCAL, 'r') as f:
            my_dict = json.load(f)

        self.all_country_profiles = my_dict['country_profiles']

    def get_country_list(self):
        try:
            self.country_codes = self.all_country_profiles[self.country_profile]["country_codes"]
        except:
            print("Country profile does not exist")
            sys.exit()

        # Get exclusions
        profile = self.all_country_profiles[self.country_profile]
        try:
            self.exclusion_check = profile["exclusion_check"]
        except:
            self.exclusion_check = ""

        # Get agreement name
        self.agreement_name = profile["agreement_name"]

        self.agreement_date_short = profile["agreement_date"]
        temp = datetime.strptime(self.agreement_date_short, "%d/%m/%Y")
        self.agreement_date_long = datetime.strftime(temp, "%d %B %Y").lstrip("0")

        self.table_per_country = profile["table_per_country"]
        self.version = profile["version"]
        self.country_name = profile["country_name"]

    def get_sections_chapters(self):
        # MPP: TODO Section chapters not used removed from create_fta

        rows_sections_chapters = self.execute_sql(GET_SECTIONS_CHAPTERS_SQL, dict_cursor=True)
        for rd in rows_sections_chapters:
            self.section_chapter_list.append([rd['chapter'], ['section_id'], False])

        # The last parameter is "1" if the chapter equates to a new section
        iLastSection = -1
        for r in self.section_chapter_list:
            iSection = r[1]
            if iSection != iLastSection:
                r[2] = True
            iLastSection = iSection

    def readTemplates(self, has_quotas):
        self.COMPONENT_DIR = os.path.join(self.COMPONENT_DIR, "")
        if has_quotas:
            fDocument = open(os.path.join(self.COMPONENT_DIR, "document_hasquotas.xml"), "r")
        else:
            fDocument = open(os.path.join(self.COMPONENT_DIR, "document_noquotas.xml"), "r")
        self.sDocumentXML = fDocument.read()
        self.sDocumentXML = self.sDocumentXML.replace("{AGREEMENT_NAME}", self.agreement_name)
        self.sDocumentXML = self.sDocumentXML.replace("{VERSION}", self.version)
        self.sDocumentXML = self.sDocumentXML.replace("{AGREEMENT_DATE}", self.agreement_date_long)
        self.sDocumentXML = self.sDocumentXML.replace(
            "{AGREEMENT_DATE_SHORT}", self.agreement_date_short,
        )
        self.sDocumentXML = self.sDocumentXML.replace("{COUNTRY_NAME}",	self.country_name)

        fFootnoteTable = open(os.path.join(self.COMPONENT_DIR, "table_footnote.xml"), "r")
        self.sFootnoteTableXML = fFootnoteTable.read()

        fFootnoteTableRow = open(os.path.join(self.COMPONENT_DIR, "tablerow_footnote.xml"), "r")
        self.sFootnoteTableRowXML = fFootnoteTableRow.read()

        fHeading1 = open(os.path.join(self.COMPONENT_DIR, "heading1.xml"), "r")
        self.sHeading1XML = fHeading1.read()

        fHeading2 = open(os.path.join(self.COMPONENT_DIR, "heading2.xml"), "r")
        self.sHeading2XML = fHeading2.read()

        fHeading3 = open(os.path.join(self.COMPONENT_DIR, "heading3.xml"), "r")
        self.sHeading3XML = fHeading3.read()

        fPara = open(os.path.join(self.COMPONENT_DIR, "paragraph.xml"), "r")
        self.sParaXML = fPara.read()

        fBullet = open(os.path.join(self.COMPONENT_DIR, "bullet.xml"), "r")
        self.sBulletXML = fBullet.read()

        fBanner = open(os.path.join(self.COMPONENT_DIR, "banner.xml"), "r")
        self.sBannerXML = fBanner.read()

        fPageBreak = open(os.path.join(self.COMPONENT_DIR, "pagebreak.xml"), "r")
        self.sPageBreakXML = fPageBreak.read()

        fTable = open(os.path.join(self.COMPONENT_DIR, "table_schedule.xml"), "r")
        fTableRow = open(os.path.join(self.COMPONENT_DIR, "tablerow_schedule.xml"), "r")

        self.sTableXML = fTable.read()
        self.sTableRowXML = fTableRow.read()

        # Get quota templates
        fQuotaTable = open(os.path.join(self.COMPONENT_DIR, "table_quota.xml"), "r")
        fQuotaTableRow = open(os.path.join(self.COMPONENT_DIR, "tablerow_quota.xml"), "r")

        self.sQuotaTableXML = fQuotaTable.read()
        self.sQuotaTableRowXML = fQuotaTableRow.read()

        fFootnoteReference = open(os.path.join(self.COMPONENT_DIR, "footnotereference.xml"), "r")
        self.sFootnoteReferenceXML = fFootnoteReference.read()

        # Footnote templates
        fFootnotes = open(os.path.join(self.COMPONENT_DIR, "footnotes.xml"), "r")
        self.sFootnotesXML = fFootnotes.read()

        # Horizontal line for putting dividers into the quota table
        fHorizLine = open(os.path.join(self.COMPONENT_DIR, "horiz_line.xml"), "r")
        self.sHorizLineXML = fHorizLine.read()

        # Soft horizontal line for putting dividers into the quota table
        fHorizLineSoft = open(os.path.join(self.COMPONENT_DIR, "horiz_line_soft.xml"), "r")
        self.sHorizLineSoftXML = fHorizLineSoft.read()

        # core.xml that contains document information
        fCore = open(os.path.join(self.COMPONENT_DIR, "core.xml"), "r")
        self.sCoreXML = fCore.read()

    def get_mfns_for_siv_products(self):
        print(" - Getting MFNs for SIV products")
        rows = self.execute_sql(GET_MFNS_FOR_SIV_PRODUCTS_SQL)

        for r in rows:
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
