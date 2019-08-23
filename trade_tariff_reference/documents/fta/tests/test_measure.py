from datetime import datetime

from trade_tariff_reference.documents.fta.measure import Measure


def get_measure(
    measure_sid=None,
    commodity_code=None,
    quota_order_number_id=None,
    validity_start_date=datetime.now(),
    validity_end_date=None,
    geographical_area_id=None,
    reduction_indicator=None
):
    return Measure(
        measure_sid,
        commodity_code,
        quota_order_number_id,
        validity_start_date,
        validity_end_date,
        geographical_area_id,
        reduction_indicator
    )
