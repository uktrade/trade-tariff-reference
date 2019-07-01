import functions as f

class quota_order_number(object):
	def __init__(self, quota_order_number_id):
		self.quota_order_number_id	= quota_order_number_id
		self.quota_definition_list	= []
		self.commodity_list			= []
		self.suspended				= False
		self.origin_quota			= ""
		self.addendum				= ""
		self.scope					= ""

		self.format_order_number()

	def format_order_number(self):
		#self.quota_order_number_id_formatted = self.quota_order_number_id[0:2] + "." + self.quota_order_number_id[2:]
		self.quota_order_number_id_formatted = self.quota_order_number_id
		if self.scope != "":
			self.quota_order_number_id_formatted += "</w:t></w:r><w:r><w:rPr><w:b/></w:rPr><w:br/></w:r><w:r><w:t>" + self.scope