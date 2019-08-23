from trade_tariff_reference.documents.mfn.special import Special


def test_empty_initialise():
    special = Special()
    assert special.commodity_code == ""
    assert special.note == ""


def test_initialise():
    special = Special(commodity_code=1, note='Test note')
    assert special.commodity_code == "1"
    assert special.note == "Test note"
