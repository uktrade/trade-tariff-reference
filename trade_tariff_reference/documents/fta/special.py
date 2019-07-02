# MPP: Not used

import documents.fta.functions as f


class Special:

    def __init__(self, commodity_code="", note=""):
        self.commodity_code = f.mstr(commodity_code)
        self.note = f.mstr(note)
