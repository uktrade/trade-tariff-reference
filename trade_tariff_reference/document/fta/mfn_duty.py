import re
import sys
from datetime import datetime

import functions as f
import glob as g

class mfn_duty(object):
	def __init__(self, commodity_code, duty_amount, validity_start_date, validity_end_date):
		# Get parameters from instantiator
		self.commodity_code         = commodity_code
		self.duty_amount            = duty_amount
		self.validity_start_date    = validity_start_date
		self.validity_end_date      = validity_end_date
