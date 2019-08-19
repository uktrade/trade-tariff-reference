from trade_tariff_reference.documents.mfn.seasonal import Seasonal


def test_empty_initialise():
    seasonal = Seasonal()

    assert seasonal.commodity_code == ""

    assert seasonal.season1_start == ""
    assert seasonal.season1_end == ""
    assert seasonal.season1_expression == ""

    assert seasonal.season2_start == ""
    assert seasonal.season2_end == ""
    assert seasonal.season2_expression == ""

    assert seasonal.season3_start == ""
    assert seasonal.season3_end == ""
    assert seasonal.season3_expression == ""


def test_initialise():
    seasonal = Seasonal(
        commodity_code=1,
        season1_start='1 start',
        season1_end='1 end',
        season1_expression='1 EUR',
        season2_start='2 start',
        season2_end='2 end',
        season2_expression='DTN G cups',
        season3_start='3 start',
        season3_end='3 end',
        season3_expression='things DTN',
    )

    assert seasonal.commodity_code == "1"

    assert seasonal.season1_start == "1 start"
    assert seasonal.season1_end == "1 end"
    assert seasonal.season1_expression == "1 €"

    assert seasonal.season2_start == "2 start"
    assert seasonal.season2_end == "2 end"
    assert seasonal.season2_expression == "/ 100 kg gross cups"

    assert seasonal.season3_start == "3 start"
    assert seasonal.season3_end == "3 end"
    assert seasonal.season3_expression == "things / 100 kg"
