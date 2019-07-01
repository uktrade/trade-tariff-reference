	def resolve_measures_didwork(self):
		self.duty_string = ""

		is_all_full_year	= True
		contains_siv		= False
		is_infinite			= False

		for measure in self.measure_list:
			if measure.extent not in(365, -1) :
				is_all_full_year = False

			if measure.extent == -1:
				is_infinite = True

			if "Entry Price" in measure.combined_duty:
				contains_siv = True

		# Check to see if this is a full year measure
		
		# If it is, then only show the chronologically last duty, as any others will be from a previous year
		# Also check to see if this is on the entry price system. If this is EPS, then it is not going to
		# be seasonal as well - they appear to be mutually exclusive

		if is_all_full_year == True or contains_siv == True:
			measure_count = len(self.measure_list)

			if measure_count > 0:
				for i in range(0, measure_count):
					if i != measure_count - 1:
						measure = self.measure_list[i]
						#measure.suppress = True


		# So if the measure is neither infinite, nor entry price, nor is it a full year measure
		# Then it must be seasonal
		full_period_list	= []
		for measure in self.measure_list:
			if (contains_siv == False) and (is_all_full_year == False) and (is_infinite == False):
				obj_period = str(measure.validity_start_day) + "/" + str(measure.validity_start_month)
				full_period_list.append(obj_period)


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
		if (contains_siv == False) and (is_all_full_year == False) and (is_infinite == False):
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

		for measure in self.measure_list:
			if measure.suppress == False:
				if is_seasonal:
					self.duty_string = measure.xml_with_dates() + self.duty_string
				else:
					self.duty_string += measure.combined_duty

