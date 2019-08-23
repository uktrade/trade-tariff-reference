from trade_tariff_reference.documents.fta.local_siv import LocalSiv


def test_local_siv_initialise():
    local_siv = LocalSiv(
        1, 2, 3, 4, 5
    )
    assert local_siv.goods_nomenclature_item_id == 1
    assert local_siv.validity_start_date == 2
    assert local_siv.condition_duty_amount == 3
    assert local_siv.condition_monetary_unit_code == 4
    assert local_siv.condition_measurement_unit_code == 5
