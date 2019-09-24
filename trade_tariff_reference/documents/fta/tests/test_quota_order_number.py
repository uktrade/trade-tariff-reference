
from trade_tariff_reference.documents.fta.quota_order_number import QuotaOrderNumber


def test_format_order_string():
    quota_order_number = QuotaOrderNumber(1)
    assert quota_order_number.quota_order_number_id_formatted == '1'


def test_format_order_string_when_scope_set():
    quota_order_number = QuotaOrderNumber(1)
    quota_order_number.scope = 'Scope'
    quota_order_number.format_order_number()
    assert (
        quota_order_number.quota_order_number_id_formatted
        == '1 Scope'
    )
