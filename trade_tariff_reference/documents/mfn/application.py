import sys
import os
from os import system, name 
import csv


from .seasonal import Seasonal
from .special import Special

from trade_tariff_reference.documents.database import DatabaseConnect


class Application(DatabaseConnect):

	def __init__(self):
		self.authoriseduse_list		= []
		self.seasonal_list			= []
		self.special_list			= []
		self.latin_phrases			= []
		self.section_chapter_list	= []
		self.debug					= False
		self.suppress_duties		= False

		self.BASE_DIR			= os.path.dirname(os.path.abspath(__file__))
		self.SOURCE_DIR			= os.path.join(self.BASE_DIR, 	"source")
		self.TEMP_DIR			= os.path.join(self.BASE_DIR, 	"temp")
		self.CHAPTER_NOTES_DIR	= os.path.join(self.SOURCE_DIR, "chapter_notes")
		self.COMPONENT_DIR		= os.path.join(self.BASE_DIR, 	"xmlcomponents")
		self.MODEL_DIR			= os.path.join(self.BASE_DIR, 	"model")
		self.CONFIG_DIR			= os.path.join(self.BASE_DIR, 	"..")
		self.CONFIG_DIR			= os.path.join(self.CONFIG_DIR, "fta")
		self.CONFIG_DIR			= os.path.join(self.CONFIG_DIR, "config")
		self.CONFIG_FILE		= os.path.join(self.CONFIG_DIR, "config_common.json")
		self.CONFIG_FILE_LOCAL	= os.path.join(self.CONFIG_DIR, "config_migrate_measures_and_quotas.json")

		self.connect()
		self.get_latin_terms()
		

		# Define the parameters - document type
		try:
			self.document_type = sys.argv[1]
			if self.document_type == "s":
				self.document_type = "schedule"
			if self.document_type == "c":
				self.document_type = "classification"
		except:
			self.document_type = "schedule"

		self.OUTPUT_DIR			= os.path.join(self.BASE_DIR,	"output")
		self.OUTPUT_DIR			= os.path.join(self.OUTPUT_DIR, self.document_type)

		# Define the parameters - first chapter
		try:
			self.first_chapter = int(sys.argv[2])
		except:
			self.first_chapter = 1
			self.last_chapter = 99
			
		# Define the parameters - last chapter
		try:
			self.last_chapter   = int(sys.argv[3])
		except:
			self.last_chapter   = self.first_chapter
		if self.last_chapter > 99:
			self.last_chapter = 99
			
		if (self.document_type != "classification" and self.document_type != "schedule"):
			self.document_type = "schedule"

		self.clear()

	def get_latin_terms(self):
		latin_folder	= os.path.join(self.SOURCE_DIR,	"latin")
		latin_file		= os.path.join(latin_folder, 	"latin_phrases.txt")
		with open(latin_file, "r") as f:
			reader = csv.reader(f)
			temp = list(reader)
		
		for row in temp:
			latin_phrase	= row[0]
			self.latin_phrases.append(latin_phrase)

	def clear(self): 
		# for windows 
		if name == 'nt': 
			_ = system('cls') 
		# for mac and linux(here, os.name is 'posix') 
		else: 
			_ = system('clear')

	def get_sections_chapters(self):
		# Function determines which chapters belong to which sections
		sql = """
		SELECT LEFT(gn.goods_nomenclature_item_id, 2) as chapter, cs.section_id
		FROM chapters_sections cs, goods_nomenclatures gn
		WHERE cs.goods_nomenclature_sid = gn.goods_nomenclature_sid
		AND gn.producline_suffix = '80'
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


	def read_templates(self):
		self.COMPONENT_DIR = os.path.join(self.COMPONENT_DIR, "")

		# Main document templates
		if self.document_type == "classification":
			fDocument = open(os.path.join(self.COMPONENT_DIR, "document_classification.xml"), "r")
		else:
			fDocument = open(os.path.join(self.COMPONENT_DIR, "document_schedule.xml"), "r")
		self.document_xml_string = fDocument.read()

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

		if (self.document_type == "classification"):
			fTable    = open(os.path.join(self.COMPONENT_DIR, "table_classification.xml"), "r") 
			fTableRow = open(os.path.join(self.COMPONENT_DIR, "tablerow_classification.xml"), "r") 
		else:
			fTable    = open(os.path.join(self.COMPONENT_DIR, "table_schedule.xml"), "r") 
			fTableRow = open(os.path.join(self.COMPONENT_DIR, "tablerow_schedule.xml"), "r") 

		self.table_xml_string = fTable.read()
		self.sTableRowXML = fTableRow.read()


	def get_authorised_use_commodities(self):
		# This function is required - this is used to identify any commodity codes
		# where there has been a 105 measure type assigned since the start of 2018
		# (up to the end of 2019), i.e. taking into account the measures that were
		# in place before No Deal Brexit

		# If a commodity code has a 105 instead of a 103 assigned to it, this means that there is
		# a need to insert an authorised use message in the notes column for the given commodity

		sql = """SELECT DISTINCT goods_nomenclature_item_id FROM ml.v5_2019 m WHERE measure_type_id = '105' ORDER BY 1;"""
		cur = self.conn.cursor()
		cur.execute(sql)
		rows = cur.fetchall()
		for r in rows:
			self.authoriseduse_list.append(r[0])
		
		# Also add in cucumbers: the data cannot find these, therefore manually added, 
		# as per instruction from David Owen
		self.authoriseduse_list.append("0707000510")
		self.authoriseduse_list.append("0707000520")
		
	def get_special_notes(self):
		# This function is required - it looks in the file special_notes.csv
		# and finds a list of commodities with 'special 'notes that go alongside them
		# In actual fact, there is only one record in here at the point of
		# writing this note - 5701109000,"Dutiable surface shall not include the heading,
		# the selvedges and the fringes"

		# We may need to consider how we manage this CSV file

		filename = os.path.join(self.SOURCE_DIR, "special_notes.csv")
		with open(filename, "r") as f:
			reader = csv.reader(f)
			temp = list(reader)
		for row in temp:
			commodity_code = row[0]
			note = row[1]
			oSpecial = Special(commodity_code, note)

			self.special_list.append(oSpecial)

	def get_seasonal(self):
		filename = os.path.join(self.SOURCE_DIR, "seasonal_commodities.csv")
		with open(filename, "r") as f:
			reader = csv.reader(f)
			temp = list(reader)
		for row in temp:
			commodity_code = row[0]
			season1_start = row[1]
			season1_end = row[2]
			season1_expression = row[3]
			season2_start = row[4]
			season2_end = row[5]
			season2_expression = row[6]
			season3_start = row[7]
			season3_end = row[8]
			season3_expression = row[9]
			oSeasonal = Seasonal(
				commodity_code,
				season1_start,
				season1_end,
				season1_expression,
				season2_start,
				season2_end,
				season2_expression,
				season3_start,
				season3_end,
				season3_expression
			)

			self.seasonal_list.append(oSeasonal)
