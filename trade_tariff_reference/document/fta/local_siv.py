import re
import sys
from datetime import datetime

import functions as f
import glob as g

class local_siv(object):
	def __init__(self, goods_nomenclature_item_id, validity_start_date, condition_duty_amount, condition_monetary_unit_code, condition_measurement_unit_code):
		# Get parameters from instantiator
		self.goods_nomenclature_item_id         = goods_nomenclature_item_id
		self.validity_start_date                = validity_start_date
		self.condition_duty_amount              = condition_duty_amount
		self.condition_monetary_unit_code       = condition_monetary_unit_code
		self.condition_measurement_unit_code    = condition_measurement_unit_code
