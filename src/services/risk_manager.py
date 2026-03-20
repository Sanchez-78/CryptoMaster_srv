class RiskManager:

    def __init__(self):
        # multipliers (laditelné)
        self.sl_mult = 1.5
        self.tp_mult = 2.5

    def compute(self, features, price, signal):
        atr = features.get("atr_m15", 0)

        if atr == 0:
            return None, None

        # absolutní ATR (denormalizace)
        atr_abs = atr * price

        if signal == "BUY":
            stop_loss = price - atr_abs * self.sl_mult
            take_profit = price + atr_abs * self.tp_mult

        elif signal == "SELL":
            stop_loss = price + atr_abs * self.sl_mult
            take_profit = price - atr_abs * self.tp_mult

        else:
            return None, None

        return stop_loss, take_profit