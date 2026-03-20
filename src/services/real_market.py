import random


class RealMarket:

    def __init__(self):
        self.fee = 0.001  # 0.1%
        self.base_slippage = 0.0005  # 0.05%

    # =========================
    # 💰 APPLY COSTS
    # =========================
    def apply(self, price, signal):
        spread = price * 0.0003  # 0.03%
        slippage = price * (self.base_slippage * random.uniform(0.5, 2.0))

        if signal == "BUY":
            real_price = price + spread + slippage
        elif signal == "SELL":
            real_price = price - spread - slippage
        else:
            real_price = price

        return real_price

    # =========================
    # 💸 APPLY FEE
    # =========================
    def apply_fee(self, profit):
        return profit - abs(profit) * self.fee