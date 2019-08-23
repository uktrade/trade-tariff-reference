from trade_tariff_reference.documents import functions as f


class Seasonal:

    def __init__(
        self, commodity_code="", season1_start="", season1_end="", season1_expression="", season2_start="",
        season2_end="", season2_expression="", season3_start="", season3_end="", season3_expression=""
    ):
        self.commodity_code = f.mstr(commodity_code)
        self.season1_start = f.mstr(season1_start)
        self.season1_end = f.mstr(season1_end)
        self.season1_expression = f.format_seasonal_expression(season1_expression)

        self.season2_start = f.mstr(season2_start)
        self.season2_end = f.mstr(season2_end)
        self.season2_expression = f.format_seasonal_expression(season2_expression)

        self.season3_start = f.mstr(season3_start)
        self.season3_end = f.mstr(season3_end)
        self.season3_expression = f.format_seasonal_expression(season3_expression)
