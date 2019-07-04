
class QuotaOrderNumber:

    def __init__(self, quota_order_number_id):
        self.quota_order_number_id = quota_order_number_id
        self.quota_definition_list = []
        self.commodity_list = []
        self.suspended = False
        self.origin_quota = ""
        self.addendum = ""
        self.scope = ""
        self.format_order_number()

    def format_order_number(self):
        # MPP: TODO This does not seem be doing anything as scope is always ""
        # self.quota_order_number_id_formatted = self.quota_order_number_id[0:2] + "." + self.quota_order_number_id[2:]
        html = "</w:t></w:r><w:r><w:rPr><w:b/></w:rPr><w:br/></w:r><w:r><w:t>"
        self.quota_order_number_id_formatted = self.quota_order_number_id
        if self.scope != "":
            self.quota_order_number_id_formatted += html + self.scope
