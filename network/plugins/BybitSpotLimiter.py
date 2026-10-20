class BybitSpotLimiter:
    @staticmethod
    def setLimitOrder(session, symbol, qty, price):
        session.place_order(
            category="spot",
            symbol="XRPUSDT",
            side="buy",
            orderType="Limit",
            qty=7,
            price=1,
        )