import documents.fta.functions as functions
from documents.fta.measure import period
from datetime import datetime

class commodity(object):
	def __init__(self, commodity_code):
		self.commodity_code	= functions.mstr(commodity_code)
		self.measure_list	= []
		self.duty_string	= ""
		self.suppress = False

		self.formatCommodityCode()


	def resolve_measures(self):
		date_brexit = datetime.strptime("2019-10-31", "%Y-%m-%d") # '%m/%d/%y %H:%M:%S')
		self.duty_string = ""

		is_all_full_year	= True
		is_infinite			= False

		# Check if the measure is exactly a year long; in which case only a single measure
		# can be shown - it cannot be seasonal
		for measure in self.measure_list:
			if measure.extent not in(365, 366, 730, 731, 1095, 1096, 1460, 1461, 1825, 1826, 2190, 2191, -1) :
				is_all_full_year = False

			if measure.extent == -1:
				is_infinite = True


		# If the measure is a full year measure, then we should only show one measure
		# under all circumstances; therefore remove all but the 1st item in the list
		# The 1st item is the most recent
		if is_all_full_year or is_infinite:
			measure_count = len(self.measure_list)
			if measure_count > 1:
				for i in range(1, measure_count):
					self.measure_list.pop()
			for m in self.measure_list:
				self.duty_string += m.xml_without_dates()

			#if self.commodity_code == "0210111100":
			if is_all_full_year:
				if self.measure_list[0].validity_end_date != None:
					if self.measure_list[0].validity_end_date < date_brexit:
						self.suppress = True
						#print ("found an old record - kill it", self.commodity_code)
		
		else:
			self.measure_list.reverse()
			full_period_list	= []
			for m in self.measure_list:
				full_period_list.append(m.period_start)

			if len(full_period_list) > 0:
				partial = set(full_period_list)
			else:
				partial = []

			partial_period_list = []

			if len(partial) > 0:
				for obj in partial:
					obj_split = obj.split("/")
					obj_period = period(int(obj_split[0]), int(obj_split[1]))
					partial_period_list.append(obj_period)

			reversed_list = self.measure_list
			reversed_list.reverse()

			is_seasonal = False
			if (is_all_full_year == False) and (is_infinite == False):
				is_seasonal = True
				for measure in reversed_list:
					for obj in partial_period_list:
						if obj.marked == False:
							if int(measure.validity_start_day) == int(obj.validity_start_day) and int(measure.validity_start_month) == int(obj.validity_start_month):
								measure.marked = True
								obj.marked = True

				for measure in reversed_list:
					if measure.marked == False:
						measure.suppress = True


			for i in range(len(self.measure_list) - 1, 0, -1):
				measure = self.measure_list[i]
				if measure.suppress == True:
					self.measure_list.pop(i)


			
			

			# Before finally writing the items to a list, we need to look at contiguous items
			# that have the same duty and combine
			self.measure_list.reverse()
			measure_count = len(self.measure_list)

			if measure_count > 1:
				for i in range(measure_count - 2, -1, -1):
					m1 = self.measure_list[i]
					m2 = self.measure_list[i + 1]
					#if m1 finished a day before m2 starts
					delta = (m2.validity_start_date - m1.validity_end_date).days
					if (delta == 1) and (m1.combined_duty == m2.combined_duty):
						m1.period_end	= m2.period_end
						m1.period		= m1.period_start + " to " + m1.period_end
						m1.validity_end_date = m2.validity_end_date
						m1.extent = (m1.validity_end_date - m1.validity_start_date).days + 1

						self.measure_list.pop(i + 1)


			# A final check that this concatenation of measures has not actually generated a single measure
			# This is the case with product 0702000000 for Palestine, also Canada
			measure_count = len(self.measure_list)
			
			if measure_count == 1:
				if m.validity_end_date < date_brexit:
					print ("Found a single measure that ends before Brexit", self.commodity_code)
					self.suppress = True
				m = self.measure_list[0]
				
				if m.extent in (365, 366, -1):
					self.duty_string = m.xml_without_dates() + self.duty_string
				else:
					self.duty_string = m.xml_with_dates() + self.duty_string
			else:
				for measure in self.measure_list:
					self.duty_string += measure.xml_with_dates()
				

	def formatCommodityCode(self):
		s = self.commodity_code

		if s[4:10] == "000000":
			self.commodity_code_formatted = s[0:4] + ' 00 00'
		elif s[6:10] == "0000":
			self.commodity_code_formatted = s[0:4] + ' ' + s[4:6] + ' 00'
		elif s[8:10] == "00":
			self.commodity_code_formatted = s[0:4] + ' ' + s[4:6] + ' ' + s[6:8]
		else:
			self.commodity_code_formatted = s[0:4] + ' ' + s[4:6] + ' ' + s[6:8] + ' ' + s[8:10]
