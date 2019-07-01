import sys
import os
from os import system, name 
import csv
import json
from datetime import datetime

from .database import DatabaseConnect
from .document import document
from .hierarchy import hierarchy
from .mfn_duty import mfn_duty
from .local_siv import local_siv


class Application(DatabaseConnect):
	def __init__(self):
		self.clear()
		self.siv_list               = []
		self.meursing_list			= []
		self.vessels_list           = []
		self.civilair_list			= []
		self.airworthiness_list		= []
		self.aircraft_list			= []
		self.pharmaceuticals_list	= []
		self.ita_list 				= []
		self.generalrelief_list		= []
		self.authoriseduse_list		= []
		self.seasonal_list			= []
		self.special_list			= []
		self.section_chapter_list	= []
		self.lstFootnotes			= []
		self.lstFootnotesUnique		= []
		self.debug					= False
		self.suppress_duties		= False
		self.country_codes			= ""
		self.siv_data_list			= []
		self.seasonal_fta_duties	= []
		self.meursing_components		= []
		
		self.partial_temporary_stops	= []

		self.BASE_DIR			= os.path.dirname(os.path.abspath(__file__))
		self.SOURCE_DIR			= os.path.join(self.BASE_DIR, "source")
		self.CSV_DIR			= os.path.join(self.BASE_DIR, "csv")
		self.COMPONENT_DIR		= os.path.join(self.BASE_DIR, "xmlcomponents")

		self.CONFIG_DIR			= os.path.join(self.CONFIG_DIR, "config")
		self.CONFIG_FILE		= os.path.join(self.CONFIG_DIR, "config_common.json")
		self.CONFIG_FILE_LOCAL	= os.path.join(self.CONFIG_DIR, "config_migrate_measures_and_quotas.json")

		self.BALANCE_FILE		= os.path.join(self.CONFIG_DIR, "quota_volume_master.csv")

		# For the word model folders
		self.MODEL_DIR			= os.path.join(self.BASE_DIR, "model")
		self.WORD_DIR			= os.path.join(self.MODEL_DIR, "word")
		self.DOCPROPS_DIR		= os.path.join(self.MODEL_DIR, "docProps")

		# For the output folders
		self.OUTPUT_DIR			= os.path.join(self.BASE_DIR, "output")

		self.get_config()

		# Unless we are running a sequence, find the country code
		if "sequence" in sys.argv[0]:
			return
		else:
			try:
				self.country_profile = sys.argv[1]
			except:
				print ("No country scope parameter found - ending")
				sys.exit()
		
		self.get_country_list()
		self.geo_ids = f.list_to_sql(self.country_codes)

	def create_document(self):
		# Create the document
		my_document = document()
		self.get_meursing_components()
		my_document.check_for_quotas()
		self.readTemplates(my_document.has_quotas)

		# Get commodities where there is a local SIV
		#print (self.geo_ids)
		
		sql = """
		SELECT DISTINCT m.goods_nomenclature_item_id, m.validity_start_date, mc.condition_duty_amount,
		mc.condition_monetary_unit_code, mc.condition_measurement_unit_code
		FROM ml.v5_2019 m, measure_conditions mc, measure_condition_components mcm
		WHERE mc.measure_sid = m.measure_sid
		AND mc.measure_condition_sid = mcm.measure_condition_sid
		AND mc.condition_code = 'V' AND geographical_area_id IN (""" + self.geo_ids + """) AND mcm.duty_amount != 0
		ORDER BY 1, 2 DESC, 3 DESC
		"""

		cur = self.conn.cursor()
		cur.execute(sql)
		rows = cur.fetchall()

		self.local_sivs						= []
		self.local_sivs_commodities_only	= []

		for rw in rows:
			goods_nomenclature_item_id		= rw[0]
			validity_start_date				= rw[1]
			condition_duty_amount			= rw[2]
			condition_monetary_unit_code	= rw[3]
			condition_measurement_unit_code	= rw[4]

			obj = local_siv(goods_nomenclature_item_id, validity_start_date, condition_duty_amount, condition_monetary_unit_code, condition_measurement_unit_code)
			self.local_sivs.append(obj)
			self.local_sivs_commodities_only.append(goods_nomenclature_item_id)
		#print (len(self.local_sivs))
		#sys.exit()
		

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
		print ("\nPROCESS COMPLETE - file written to " + my_document.FILENAME + "\n")
			
	def clear(self): 
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

		self.DBASE = "tariff_eu"
		self.p	= "tariffs"

		# Get local config items
		with open(self.CONFIG_FILE_LOCAL, 'r') as f:
			my_dict = json.load(f)

		self.all_country_profiles = my_dict['country_profiles']

		# Connect to the database
		#print (self.DBASE)
		self.connect()

	def get_country_list(self):
		try:
			self.country_codes = self.all_country_profiles[self.country_profile]["country_codes"]
		except:
			print ("Country profile does not exist")
			sys.exit()
		
		# Get exclusions
		try:
			self.exclusion_check = self.all_country_profiles[self.country_profile]["exclusion_check"]
		except:
			self.exclusion_check = ""
			pass

		#print (self.exclusion_check)
		#sys.exit()
		
		# Get agreement name
		self.agreement_name			= self.all_country_profiles[self.country_profile]["agreement_name"]

		self.agreement_date_short	= self.all_country_profiles[self.country_profile]["agreement_date"]
		temp = datetime.strptime(self.agreement_date_short, "%d/%m/%Y")
		self.agreement_date_long	= datetime.strftime(temp, "%d %B %Y").lstrip("0")

		self.table_per_country		= self.all_country_profiles[self.country_profile]["table_per_country"]
		self.version				= self.all_country_profiles[self.country_profile]["version"]
		self.country_name			= self.all_country_profiles[self.country_profile]["country_name"]


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

	def getFootnotes(self):
		# Get all footnotes
		sql = """SELECT DISTINCT fagn.goods_nomenclature_item_id, (fagn.footnote_type || fagn.footnote_id) as footnote, fd.description as footnote_description
		FROM footnote_association_goods_nomenclatures fagn, ml.ml_footnotes fd, footnote_types ft, goods_nomenclatures gn
		WHERE fagn.footnote_id = fd.footnote_id
		AND fagn.footnote_type = fd.footnote_type_id
		AND fagn.footnote_type = ft.footnote_type_id
		AND fagn.goods_nomenclature_item_id = gn.goods_nomenclature_item_id
		AND fagn.productline_suffix = gn.producline_suffix
		AND fagn.productline_suffix = '80'
		AND gn.producline_suffix = '80'
		AND fagn.goods_nomenclature_item_id LIKE '""" + sChapter + """%'
		AND ft.application_code IN ('1', '2')
		AND fagn.validity_start_date < CURRENT_DATE
		AND (fagn.validity_end_date > CURRENT_DATE OR fagn.validity_end_date IS NULL)
		AND gn.validity_start_date < CURRENT_DATE
		AND (gn.validity_end_date > CURRENT_DATE OR gn.validity_end_date IS NULL)
		ORDER BY 1, 2"""
		cur = self.conn.cursor()
		cur.execute(sql)
		rows_foonotes = cur.fetchall()
		self.lstFootnotes = list(rows_foonotes)
		self.lstFootnotesUnique = []
		for x in self.lstFootnotes:
			blFound = False
			for y in self.lstFootnotesUnique:
				if x[1] == y[0]:
					blFound = True
					break
			if blFound == False:
				self.lstFootnotesUnique.append([x[1], f.formatFootnote(x[2])])

	def readTemplates(self, has_quotas):
		self.COMPONENT_DIR = os.path.join(self.COMPONENT_DIR, "")
		if has_quotas:
			fDocument = open(os.path.join(self.COMPONENT_DIR, "document_hasquotas.xml"), "r")
		else:
			fDocument = open(os.path.join(self.COMPONENT_DIR, "document_noquotas.xml"), "r")
		self.sDocumentXML = fDocument.read()
		self.sDocumentXML = self.sDocumentXML.replace("{AGREEMENT_NAME}",		self.agreement_name)
		self.sDocumentXML = self.sDocumentXML.replace("{VERSION}",				self.version)
		self.sDocumentXML = self.sDocumentXML.replace("{AGREEMENT_DATE}",		self.agreement_date_long)
		self.sDocumentXML = self.sDocumentXML.replace("{AGREEMENT_DATE_SHORT}",	self.agreement_date_short)
		self.sDocumentXML = self.sDocumentXML.replace("{COUNTRY_NAME}",			self.country_name)

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

		fTable    = open(os.path.join(self.COMPONENT_DIR, "table_schedule.xml"), "r") 
		fTableRow = open(os.path.join(self.COMPONENT_DIR, "tablerow_schedule.xml"), "r") 

		self.sTableXML = fTable.read()
		self.sTableRowXML = fTableRow.read()

		# Get quota templates
		fQuotaTable    = open(os.path.join(self.COMPONENT_DIR, "table_quota.xml"), "r") 
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

			
	def getSeasonal(self):
		sFileName = os.path.join(self.SOURCE_DIR, "seasonal_commodities.csv")
		with open(sFileName, "r") as f:
			reader = csv.reader(f)
			temp = list(reader)
		for row in temp:
			commodity_code		= row[0]
			season1_start		= row[1]
			season1_end			= row[2]
			season1_expression	= row[3]
			season2_start		= row[4]
			season2_end			= row[5]
			season2_expression	= row[6]
			season3_start		= row[7]
			season3_end			= row[8]
			season3_expression	= row[9]
			oSeasonal = seasonal(commodity_code, season1_start, season1_end, season1_expression, season2_start, season2_end, season2_expression, season3_start, season3_end, season3_expression)

			self.seasonal_list.append(oSeasonal)

	def getSIVProducts(self):
		# The SQL below gets all products that have a V condition, therefore entry price system against them
		"""SELECT DISTINCT goods_nomenclature_item_id FROM measures m, measure_conditions mc
		WHERE m.measure_sid = mc.measure_sid
		AND mc.condition_code = 'V'
		AND m.validity_start_date >= '2018-01-01' AND (m.validity_end_date <= '2020-01-01' OR m.validity_end_date IS NULL)
		ORDER BY 1"""
		sFileName = os.path.join(self.SOURCE_DIR, "siv_products.csv")
		with open(sFileName, "r") as f:
			reader = csv.reader(f)
			temp = list(reader)
		for i in temp:
			self.siv_list.append(i[0])

	def getCountryAdValoremForSIV(self):
		sql = """SELECT m.goods_nomenclature_item_id, mcc.duty_amount, mcc.duty_expression_id, m.validity_start_date, m.validity_end_date
		FROM measures m, measure_conditions mc, measure_condition_components mcc
		WHERE m.measure_sid = mc.measure_sid
		AND mcc.measure_condition_sid = mc.measure_condition_sid
		AND m.geographical_area_id IN (""" + self.geo_ids + """)
		AND mc.condition_code = 'V'
		AND mcc.duty_expression_id = '01'
		AND validity_start_date <= CURRENT_DATE
		AND (validity_end_date >= CURRENT_DATE OR validity_end_date IS NULL)
		ORDER BY validity_start_date DESC"""
		#print (sql)
		cur = self.conn.cursor()
		cur.execute(sql)
		rows = cur.fetchall()
		self.partial_temporary_stops = []
		for rw in rows:
			goods_nomenclature_item_id	= rw[0]
			duty_amount					= rw[1]
			duty_expression_id			= rw[2]
			validity_start_date			= rw[3]
			validity_end_date			= rw[4]

			siv = siv_data(goods_nomenclature_item_id, duty_amount, duty_expression_id, validity_start_date, validity_end_date)
			self.siv_data_list.append (siv)

		# Ensure that there is only one (the latest record listed here; delete all the others)
		unique_siv_data_list_commodities_only	= []
		unique_siv_data_list					= []
		for item in self.siv_data_list:
			if item.goods_nomenclature_item_id not in unique_siv_data_list_commodities_only:
				unique_siv_data_list.append (item)

			unique_siv_data_list_commodities_only.append (item.goods_nomenclature_item_id)

		self.siv_data_list = unique_siv_data_list
		
	def getMeursingProducts(self):
		# The SQL below gets all products that have a V condition, therefore entry price system against them
		"""SELECT DISTINCT goods_nomenclature_item_id FROM measures m, measure_conditions mc
		WHERE m.measure_sid = mc.measure_sid
		AND mc.condition_code = 'V'
		AND m.validity_start_date >= '2018-01-01' AND (m.validity_end_date <= '2020-01-01' OR m.validity_end_date IS NULL)
		ORDER BY 1"""
		sFileName = os.path.join(self.SOURCE_DIR, "meursing_products.csv")
		with open(sFileName, "r") as f:
			reader = csv.reader(f)
			temp = list(reader)
		for i in temp:
			self.meursing_list.append(i[0])

	def getSeasonalProducts(self):
		sFileName = os.path.join(self.SOURCE_DIR, "seasonal_fta_duties.csv")
		with open(sFileName, "r") as f:
			reader = csv.reader(f)
			file = list(reader)

		for row in file:
			goods_nomenclature_item_id	= row[0]
			geographical_area_id		= row[1]
			extent						= row[2]
			duty						= row[3]

			s = seasonal_small(goods_nomenclature_item_id, geographical_area_id, extent, duty)
			self.seasonal_fta_duties.append(s)

	def get_mfn_duty(self, goods_nomenclature_item_id, validity_start_date, validity_end_date):
		productline_suffix = "80"
		sql = """SELECT goods_nomenclature_item_id, producline_suffix as productline_suffix, number_indents,
		description FROM ml.goods_nomenclature_export('""" + goods_nomenclature_item_id + """') WHERE producline_suffix = '80';"""
		#print (sql)
		cur = self.conn.cursor()
		cur.execute(sql)
		rows = cur.fetchall()
		for row in rows:
			number_indents = row[2]
			description = row[3]
			print (number_indents)
			hier = hierarchy(goods_nomenclature_item_id, productline_suffix, number_indents, description)
			hier.get_hierarchy("up")
			clause = ""
			for o in hier.ar_hierarchies:
				print (o.goods_nomenclature_item_id, o.productline_suffix)
				if o.productline_suffix == "80":
					clause += "'" + o.goods_nomenclature_item_id + "', "
			clause = clause.strip()
			clause = clause.strip(",")
			print (clause)

		sql = """SELECT * FROM measures WHERE goods_nomenclature_item_id IN (""" + clause + """) AND measure_type_id IN ('103', '105')
		AND validity_start_date < '2019-10-31' AND (validity_end_date >= '2019-10-31' OR validity_end_date IS NULL)"""
		#print (sql)

	def list_to_where_clause_numeric(self, my_list):
		s = ""
		for obj in my_list:
			s += str(obj) + ", "
		s = s.strip()
		s = s.strip(",")
		return (s)

	def get_mfns_for_siv_products(self):
		print (" - Getting MFNs for SIV products")

		sql = """SELECT DISTINCT m.goods_nomenclature_item_id, mcc.duty_amount, m.validity_start_date, m.validity_end_date
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
			goods_nomenclature_item_id	= r[0]
			duty_amount					= r[1]
			validity_start_date			= r[2]
			validity_end_date			= r[3]
			mfn = mfn_duty(goods_nomenclature_item_id, duty_amount, validity_start_date, validity_end_date)
			self.mfn_list.append(mfn)

	def get_mfn_rate(self, commodity_code, validity_start_date, validity_end_date):
		"""
		for mfn in self.mfn_list:
			if commodity_code == "0805290011":
				print (mfn.duty_amount)
			print (mfn.commodity_code, mfn.duty_amount)
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
		if found == False:
			#print ("Error matching SIVs on", commodity_code, " for date", validity_start_date)
			if commodity_code[8:10] != "00":
				commodity_code = commodity_code[0:8] + "00"
				#print (commodity_code)
				#sys.exit()
				mfn_rate = self.get_mfn_rate(commodity_code, validity_start_date, validity_end_date)
			elif commodity_code[6:10] != "0000":
				commodity_code = commodity_code[0:6] + "00"
				mfn_rate = self.get_mfn_rate(commodity_code, validity_start_date, validity_end_date)
				#pass
		return (mfn_rate)

	def get_meursing_components(self):
		sql = "SELECT AVG(duty_amount) FROM ml.meursing_components WHERE geographical_area_id = '1011'"
		cur = self.conn.cursor()
		cur.execute(sql)
		row = cur.fetchone()
		self.erga_omnes_average = row[0]


	def get_meursing_percentage(self, reduction_indicator, geographical_area_id):
		# Get the Erga Omnes Meursing average
		sql = """
		SELECT AVG(duty_amount) FROM ml.meursing_components WHERE geographical_area_id = '""" + geographical_area_id + """' AND reduction_indicator = """ + str(reduction_indicator)
		cur = self.conn.cursor()
		cur.execute(sql)
		row = cur.fetchone()
		reduced_average = row[0]
		try:
			reduction = round((reduced_average / self.erga_omnes_average) * 100)
		except:
			reduction = 100
		print (reduction_indicator, reduction, reduced_average, self.erga_omnes_average)
		return (reduction)
