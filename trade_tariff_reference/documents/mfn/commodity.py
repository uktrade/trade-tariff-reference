from trade_tariff_reference.documents import functions as f
import re

app = f.app


class Commodity:
	def __init__(self, commodity_code="", description="", product_line_suffix="", indents=0, leaf=0):
		# Get parameters from instantiator
		self.commodity_code               = commodity_code
		self.description                  = description
		self.product_line_suffix          = product_line_suffix
		self.indents                      = indents
		self.leaf                         = leaf
		self.assigned                     = False
		self.combined_duty          = ""
		self.notes_list				= []
		self.notes_string			= ""
		self.duty_list              = []
		self.suppress_row			= False
		self.suppress_duty			= False
		self.indent_string          = ""
		self.significant_children   = False
		self.measure_count          = 0
		self.measure_type_count     = 0
		
		self.format_description()
		self.get_significant_digits()
		self.get_indent_string()
		self.format_commodity_code()
		self.child_duty_list = []

		self.special_list = []

	def combine_notes(self):
		if len(self.notes_list) > 1:
			#print ("More than one note", self.commodity_code)
			#sys.exit()
			pass
		self.notes_list.sort(reverse = True)
		if len(self.notes_list) == 0:
			self.notes_string = "<w:r><w:t></w:t></w:r>"
		else:
			#print ("combine notes")
			self.notes_string = ""
			i = 1
			break_string = "<w:br/>"
			for n in self.notes_list:
				if i > 1:
					break_string = "<w:br/>"
				else:
					break_string = ""
				self.notes_string += "<w:r>" + break_string + "<w:t>" + n + "</w:t></w:r>"
				#print (n)
				i = i + 1
				

	def combine_duties(self):
		self.combined_duty      = ""

		self.measure_list         = []
		self.measure_type_list    = []
		self.additional_code_list = []

		for d in self.duty_list:
			self.measure_type_list.append(d.measure_type_id)
			self.measure_list.append(d.measure_sid)
			self.additional_code_list.append(d.additional_code_id)

		measure_type_list_unique    = set(self.measure_type_list)
		measure_list_unique         = set(self.measure_list)
		additional_code_list_unique = set(self.additional_code_list)

		self.measure_count      = len(measure_list_unique)
		self.measure_type_count = len(measure_type_list_unique)
		self.additional_code_count = len(additional_code_list_unique)
		
		if self.measure_count == 1 and self.measure_type_count == 1 and self.additional_code_count == 1:
			for d in self.duty_list:
				self.combined_duty += d.duty_string + " "
		else:
			if self.measure_type_count > 1:
				#self.combined_duty = "More than one measure type"
				if "105" in measure_type_list_unique:
					for d in self.duty_list:
						if d.measure_type_id == "105":
							self.combined_duty += d.duty_string + " "
			elif self.additional_code_count > 1:
				#self.combined_duty = "More than one additional code"
				if "500" in additional_code_list_unique:
					for d in self.duty_list:
						if d.additional_code_id == "500":
							self.combined_duty += d.duty_string + " "
				if "550" in additional_code_list_unique:
					for d in self.duty_list:
						if d.additional_code_id == "550":
							self.combined_duty += d.duty_string + " "
	
		self.combined_duty = self.combined_duty.replace("  ", " ")
		self.combined_duty = self.combined_duty.strip()


	def latinise(self):
		# Italicise any Latin text based on the content of the file latin_phrases.txt
		my_phrases = []
		for latin_phrase in app.latin_phrases:
			latin_phrase_parts = latin_phrase.split(" ")
			if self.description.find(latin_phrase) > -1:
				if latin_phrase not in my_phrases:
					self.description = self.description.replace(latin_phrase, "</w:t></w:r><w:r><w:rPr><w:i/><w:iCs/></w:rPr><w:t>" + latin_phrase + " </w:t></w:r><w:r><w:t xml:space='preserve'>")
				for part in latin_phrase_parts:
					my_phrases.append (part)
					if "thynnus" in latin_phrase:
						my_phrases.append ("thynnus")


	def format_description(self):
		self.latinise()
		self.description = str(self.description)
		self.description = self.description.replace("|of the CN", "")
		self.description = self.description.replace("liters", "litres")
		self.description = self.description.replace("|%|", "% ")
		self.description = self.description.replace("|gram", " gram")
		self.description = self.description.replace("|g", "g")
		self.description = self.description.replace("|kg", "kg")
		self.description = self.description.replace("|", " ")
		self.description = re.sub("([0-9]) %", "\\1%", self.description)
		self.description = self.description.replace("!x!", "x")
		self.description = self.description.replace(" kg", "kg")
		self.description = self.description.replace(" -goods", " - goods")
		self.description = self.description.replace(" - ", "</w:t></w:r><w:r><w:br/><w:t xml:space='preserve'>- ")
		self.description = self.description.replace(" • ", "</w:t></w:r><w:r><w:br/><w:t xml:space='preserve'>- ")
		self.description = re.sub(r"\$(.)", r'</w:t></w:r><w:r><w:rPr><w:vertAlign w:val="superscript"/></w:rPr><w:t>\1</w:t></w:r><w:r><w:t xml:space="preserve">', self.description)

		if self.description[-3:] == "!1!":
			self.description = self.description[:-3]
		self.description = self.description.replace("\r\r", "\r")
		self.description = self.description.replace("\r\n", "\n")
		self.description = self.description.replace("\n\r", "\n")
		self.description = self.description.replace("\n\n", "\n")
		self.description = self.description.replace("\r", "\n")
		self.description = self.description.replace("\n", "</w:t></w:r><w:r><w:br/></w:r><w:r><w:t>")
		self.description = self.description.replace("!1!", "</w:t></w:r><w:r><w:br/></w:r><w:r><w:t>")
		self.description = self.description.replace("  ", " ")
		self.description = self.description.replace("!o!", chr(176))
		self.description = self.description.replace("\xA0", " ")
		self.description = self.description.replace(" %", "%")
		self.description = ("<w:t>-</w:t><w:tab/>" * self.indents) + "<w:t xml:space='preserve'>" + self.description + "</w:t>"

		# Superscripts
		self.description = re.sub("<w:t>(.*)m2</w:t>", "<w:t>\g<1>m</w:t></w:r><w:r><w:rPr><w:vertAlign w:val=\"superscript\"/></w:rPr><w:t>2</w:t>", self.description, flags=re.MULTILINE)
		self.description = re.sub("<w:t>(.*)m3</w:t>", "<w:t xml:space='preserve'>\g<1>m</w:t></w:r><w:r><w:rPr><w:vertAlign w:val=\"superscript\"/></w:rPr><w:t>3</w:t>", self.description, flags=re.MULTILINE)
		self.description = re.sub("<w:t>(.*)K2O</w:t>", "<w:t>\g<1>K</w:t></w:r><w:r><w:rPr><w:vertAlign w:val=\"subscript\"/></w:rPr><w:t>2</w:t></w:r><w:r><w:t>O</w:t>", self.description, flags=re.MULTILINE)
		self.description = re.sub("<w:t>(.*)H2O2</w:t>", "<w:t>\g<1>H</w:t></w:r><w:r><w:rPr><w:vertAlign w:val=\"subscript\"/></w:rPr><w:t>2</w:t></w:r><w:r><w:t>O</w:t></w:r><w:r><w:rPr><w:vertAlign w:val=\"subscript\"/></w:rPr><w:t>2</w:t>", self.description, flags=re.MULTILINE)
		self.description = re.sub("<w:t>(.*)P2O5</w:t>", "<w:t>\g<1>P</w:t></w:r><w:r><w:rPr><w:vertAlign w:val=\"subscript\"/></w:rPr><w:t>2</w:t></w:r><w:r><w:t>O</w:t></w:r><w:r><w:rPr><w:vertAlign w:val=\"subscript\"/></w:rPr><w:t>5</w:t>", self.description, flags=re.MULTILINE)
		
		# Subscripts
		self.description = re.sub("@(.)", '</w:t></w:r><w:r><w:rPr><w:vertAlign w:val="subscript"/></w:rPr><w:t xml:space="preserve">\\1</w:t></w:r><w:r><w:t xml:space="preserve">', self.description, flags=re.MULTILINE)



		if (self.indents < 2): # Make it bold
			self.description = "<w:rPr><w:b/></w:rPr>" + self.description
			self.description = self.description.replace("<w:r><w:rPr><w:i/><w:iCs/></w:rPr>", "<w:r><w:rPr><w:i/><w:b/><w:iCs/></w:rPr>")
			self.description = self.description.replace("<w:r>", "<w:r><w:rPr><w:b/></w:rPr>")
		self.description = self.description.replace(" </w:t></w:r><w:r><w:t xml:space='preserve'>,", "</w:t></w:r><w:r><w:t xml:space='preserve'>,")
		self.description = self.description.replace("€ ", "€")

		self.description = self.description.replace("<w:r><w:br/></w:r><w:r><w:t> </w:t></w:r><w:r><w:br/></w:r>", "<w:r><w:br/></w:r><w:r><w:t> </w:t></w:r>")
		 

	def get_significant_digits(self):
		if self.commodity_code[-8:] == '00000000':
			self.significant_digits = 2
		elif self.commodity_code[-6:] == '000000':
			self.significant_digits = 4
		elif self.commodity_code[-4:] == '0000':
			self.significant_digits = 6
		elif self.commodity_code[-2:] == '00':
			self.significant_digits = 8
		else:
			self.significant_digits = 10
		

	def get_indent_string(self):
		indent_list      	= [0, 113, 227, 340, 454, 567, 680, 794, 907, 1020, 1134, 1247, 1361]
		self.indent_string	= "<w:ind w:left=\"" + str(indent_list[self.indents]) + "\" w:hanging=\"" + str(indent_list[self.indents]) + "\"/>"


	def format_commodity_code(self):
		s = self.commodity_code
		if self.product_line_suffix != "80":
			self.commodity_code_formatted = ""
		else:
			if s[4:10] == "000000":
				self.commodity_code_formatted = s[0:4]
			elif s[6:10] == "0000":
				self.commodity_code_formatted = s[0:4] + ' ' + s[4:6]
			elif s[8:10] == "00":
				self.commodity_code_formatted = s[0:4] + ' ' + s[4:6] + ' ' + s[6:8]
			else:
				self.commodity_code_formatted = s[0:4] + ' ' + s[4:6] + ' ' + s[6:8] + ' ' + s[8:10]

		#self.commodity_code_formatted = self.commodity_code + ":" + str(self.indents)
		
	def check_for_mixture(self):
		#print ("Checking for Mixture")
		my_chapter		= self.commodity_code[0:2]
		my_subheading	= self.commodity_code[0:4]
		right_chars		= self.commodity_code[-2:]
		if (my_chapter in ('02', '10', '11') or my_subheading in ('0904', '0905', '0906', '0907', '0908', '0909', '0910')) and right_chars == "00":
			if self.combined_duty == "":
				pass
			else:
				if self.combined_duty == "AU":
					self.notes_list.append("Mixture rule; non-mixture")
					self.combined_duty = "<w:r><w:t>Formula</w:t></w:r><w:r><w:br/><w:t>AU</w:t></w:r>"
				else:
					self.notes_list.append("Mixture rule; non-mixture: " + self.combined_duty)
					self.combined_duty = "Formula"
				self.assigned = True
				self.special_list.append("mixture")


	def check_for_specials(self):
		#print ("Checking for specials")
		if len(app.special_list) > 0:
			for n in app.special_list:
				if n.commodity_code == self.commodity_code:
					self.notes_list.append(n.note)
					self.assigned = True
					self.special_list.append("special")
					#print ("Adding a special on", self.commodity_code)

	def check_for_authorised_use(self):
		if self.commodity_code in app.authoriseduse_list:
			if self.product_line_suffix == "80":
				if len(self.special_list) == 0:
					if len(self.notes_list) != 0:
						print (self.notes_list)
					self.notes_list.append("Code reserved for authorised use; the duty rate is specified under regulations made under section 19 of the Taxation (Cross-border Trade) Act 2018")
					self.combined_duty = "AU"
					self.assigned = True
					self.special_list.append("authoriseduse")
		

	def check_for_seasonal(self):
		#print ("Checking for seasonal commodities")
		seasonal_records = 0
		for s in app.seasonal_list:
			if self.commodity_code == s.commodity_code and self.product_line_suffix == "80":
				seasonal_records += 1
				season1_start          = s.season1_start
				season1_end            = s.season1_end
				season1_expression     = s.season1_expression

				season2_start          = s.season2_start
				season2_end            = s.season2_end
				season2_expression     = s.season2_expression

				season3_start          = s.season3_start
				season3_end            = s.season3_end
				season3_expression     = s.season3_expression

				self.combined_duty = ""
				whitespace = "<w:tab/>"
				if season1_expression != "":
					self.combined_duty += "<w:r><w:t>" + season1_start + " to " + season1_end + "</w:t></w:r><w:r>" + whitespace + "<w:t>" + season1_expression + "</w:t></w:r>"
				if season2_expression != "":
					self.combined_duty += "<w:r><w:br/></w:r><w:r><w:t>" + season2_start + " to " + season2_end + "</w:t></w:r><w:r>" + whitespace + "<w:t>" + season2_expression + "</w:t></w:r>"
				if season3_expression != "":
					self.combined_duty += "<w:r><w:br/></w:r><w:r><w:t>" + season3_start + " to " + season3_end + "</w:t></w:r><w:r>" + whitespace + "<w:t>" + season3_expression + "</w:t></w:r>"

				self.notes_list.append("Seasonally variable rate")
				self.assigned = True
				self.special_list.append("seasonal")
				f.debug("Found a seasonal")
				break
		return (seasonal_records)