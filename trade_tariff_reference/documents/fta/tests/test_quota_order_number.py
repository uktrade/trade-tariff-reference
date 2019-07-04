
from trade_tariff_reference.documents.fta.quota_order_number import QuotaOrderNumber


def test_format_order_string():
    quota_order_number = QuotaOrderNumber(1)
    assert quota_order_number.quota_order_number_id_formatted == 1
