import sys
import os
import os.path
from os import system, name
import json

from datetime import datetime

import documents.fta.functions as f
from documents.fta.database import DatabaseConnect
from documents.fta.document import Document
from documents.fta.mfn_duty import MfnDuty
from documents.fta.local_siv import LocalSiv


class Application(DatabaseConnect):

    def __init__(self, country_profile):
        self.country_profile = country_profile
        self.clear()
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

        sql = """
        SELECT DISTINCT m.goods_nomenclature_item_id, m.validity_start_date,
         mc.condition_duty_amount, mc.condition_monetary_unit_code,
         mc.condition_measurement_unit_code
        FROM ml.v5_2019 m, measure_conditions mc, measure_condition_components mcm
        WHERE mc.measure_sid = m.measure_sid
        AND mc.measure_condition_sid = mcm.measure_condition_sid
        AND mc.condition_code = 'V' AND
         geographical_area_id IN (""" + self.geo_ids + """) AND mcm.duty_amount != 0
        ORDER BY 1, 2 DESC, 3 DESC
        """

        cur = self.conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()

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

    def clear(self):
        pass
        # for windows
        if name == 'nt':
            _ = system('cls')
        # for mac and linux(here, os.name is 'posix')
        else:
            _ = system('clear')

    def get_config(self):
        # Get global config items
        with open(self.CONFIG_FILE, 'r') as f:
            my_dict = json.load(f)

        # Get local config items
        with open(self.CONFIG_FILE_LOCAL, 'r') as f:
            my_dict = json.load(f)

        self.all_country_profiles = my_dict['country_profiles']

        self.connect()

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
        sql = """
        SELECT LEFT(gn.goods_nomenclature_item_id, 2) as chapter, cs.section_id
        FROM chapters_sections cs, goods_nomenclatures gn
        WHERE cs.goods_nomenclature_sid = gn.goods_nomenclature_sid AND gn.producline_suffix = '80'
        ORDER BY 1
        """
        cur = self.conn.cursor()
        cur.execute(sql)
        rows_sections_chapters = cur.fetchall()
        self.section_chapter_list = []
        for rd in rows_sections_chapters:
            sChapter = rd[0]
            iSection = rd[1]
            self.section_chapter_list.append([sChapter, iSection, False])

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

        sql = """
        SELECT DISTINCT m.goods_nomenclature_item_id,
         mcc.duty_amount, m.validity_start_date, m.validity_end_date
        FROM measures m, measure_conditions mc, measure_condition_components mcc
        WHERE mcc.measure_condition_sid = mc.measure_condition_sid
        AND m.measure_sid = mc.measure_sid
        AND mcc.duty_expression_id = '01'
        AND (m.validity_start_date > '2018-01-01')
        AND mc.condition_code = 'V'
        AND m.measure_type_id IN ('103', '105')
        AND m.geographical_area_id = '1011'
        ORDER BY m.goods_nomenclature_item_id, m.validity_start_date
        """
        cur = self.conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        self.mfn_list = []
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

    def get_mfn_rate(self, commodity_code, validity_start_date, validity_end_date):
        """
        for mfn in self.mfn_list:
            if commodity_code == "0805290011":
                print(mfn.duty_amount)
            print(mfn.commodity_code, mfn.duty_amount)
        sys.exit()
        """
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
                    validity_end_date
                )
            elif commodity_code[6:10] != "0000":
                commodity_code = commodity_code[0:6] + "00"
                mfn_rate = self.get_mfn_rate(
                    commodity_code,
                    validity_start_date,
                    validity_end_date
                )
        return mfn_rate

    def get_meursing_components(self):
        sql = """
        SELECT AVG(duty_amount)
        FROM ml.meursing_components WHERE geographical_area_id = '1011'
        """
        cur = self.conn.cursor()
        cur.execute(sql)
        row = cur.fetchone()
        self.erga_omnes_average = row[0]

    def get_meursing_percentage(self, reduction_indicator, geographical_area_id):
        # Get the Erga Omnes Meursing average
        sql = """
        SELECT AVG(duty_amount) FROM ml.meursing_components
         WHERE geographical_area_id = '""" + geographical_area_id + """' AND
         reduction_indicator = """ + str(reduction_indicator)
        cur = self.conn.cursor()
        cur.execute(sql)
        row = cur.fetchone()
        reduced_average = row[0]
        try:
            reduction = round((reduced_average / self.erga_omnes_average) * 100)
        except:
            reduction = 100
            print(reduction_indicator, reduction, reduced_average, self.erga_omnes_average)
        return reduction
