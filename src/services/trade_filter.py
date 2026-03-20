class TradeFilter:
    def __init__(self):
        self.min_confidence = 0.55
        self.max_open_trades = 5
        self.open_trades = 0

    def allow_trade(self, action, confidence, features):
        # ❌ HOLD nikdy neber
        if action == "HOLD":
            return False, "HOLD"

        # ❌ low confidence
        if confidence < self.min_confidence:
            return False, "LOW_CONF"

        # ❌ low volatility (slabý trh)
        vol = (
            features.get("m15_volatility", 0)
            + features.get("h1_volatility", 0)
            + features.get("h4_volatility", 0)
        )

        if vol == 0:
            return False, "NO_VOL"

        # ❌ proti hlavnímu trendu (h4)
        h4 = features.get("h4_trend", 0)

        if action == "BUY" and h4 < 0:
            return False, "AGAINST_TREND"

        if action == "SELL" and h4 > 0:
            return False, "AGAINST_TREND"

        # ❌ příliš mnoho obchodů
        if self.open_trades >= self.max_open_trades:
            return False, "MAX_TRADES"

        return True, "OK"

    def register_trade(self):
        self.open_trades += 1

    def reset(self):
        self.open_trades = 0