import functions as f
import glob as g

class partial_temporary_stop(object):
	def __init__(self, quota_order_number_id, measure_sid, validity_start_date, validity_end_date):
		self.quota_order_number_id  = quota_order_number_id
		self.measure_sid            = measure_sid
		self.validity_start_date    = validity_start_date
		self.validity_end_date      = validity_end_date
