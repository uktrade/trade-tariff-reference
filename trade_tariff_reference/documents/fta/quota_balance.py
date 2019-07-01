from dateutil.relativedelta import relativedelta
from datetime import datetime
from datetime import timedelta


class quota_balance(object):
	def __init__(self, quota_order_number_id, country, method, y1_balance, yx_balance, yx_start, measurement_unit_code, origin_quota, addendum, scope):
		self.quota_order_number_id	= quota_order_number_id
		self.country				= country
		self.method					= method
		self.y1_balance				= y1_balance
		self.yx_balance				= yx_balance
		self.yx_start				= yx_start
		self.yx_end					= self.addYear(self.yx_start)
		self.measurement_unit_code	= measurement_unit_code.strip()
		self.addendum				= addendum.strip()
		self.scope					= scope.strip()

		if origin_quota == "Y":
			origin_quota = "Yes"
		self.origin_quota			= origin_quota
		self.getY1Dates()
		
	def addYear(self, v):
		#print (type(v))
		try:
			if type(v) is str:
				d1 = datetime.strptime(v, "%d/%m/%Y")
				d2 = d1 + timedelta(days = -1)
				d2 = d2 + relativedelta(years = 1)
			else:
				d1 = v
				d2 = d1 + timedelta(days = -1)
				d2 = d2 + relativedelta(years = 1)
		except:
			#print ("An error has occurred: cannot work out date / time of quota", self.quota_order_number_id)
			#sys.exit()
			pass
		return (d2)

	def getY1Dates(self):
		dBrexit	= datetime.strptime("29/03/2019", "%d/%m/%Y")
		d1		= datetime.strptime(self.yx_start, "%d/%m/%Y")
		d1Month	= d1.month
		#print (d1Month, type(d1Month))
		#sys.exit()
		if d1Month > 3:
			self.validity_start_date_2019 = d1
			self.validity_end_date_2019 = self.addYear(self.validity_start_date_2019)
		else:
			self.validity_start_date_2019 = dBrexit
			self.validity_end_date_2019 = datetime.strptime("31/12/2019", "%d/%m/%Y")

