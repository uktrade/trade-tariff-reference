from trade_tariff_reference.documents import functions as f


class Special:

	def __init__(self, commodity_code="", note=""):
		self.commodity_code = f.mstr(commodity_code)
		self.note = f.mstr(note)
