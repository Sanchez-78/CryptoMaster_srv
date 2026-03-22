import math

class FeatureEngine:
    def __init__(self):
        self.history = {}

    def update(self, symbol, price):
        if symbol not in self.history:
            self.history[symbol] = []
        self.history[symbol].append(price)

        if len(self.history[symbol]) > 100:
            self.history[symbol].pop(0)

    def _returns(self, h, n):
        if len(h) < n + 1:
            return 0.0
        return (h[-1] - h[-n]) / h[-n]

    def _ema(self, h, period):
        if len(h) < period:
            return h[-1]
        k = 2 / (period + 1)
        ema = h[-period]
        for p in h[-period:]:
            ema = p * k + ema * (1 - k)
        return ema

    def _std(self, h, n):
        if len(h) < n:
            return 0.0
        w = h[-n:]
        m = sum(w) / n
        return (sum((x - m) ** 2 for x in w) / n) ** 0.5

    def build(self, symbol):
        h = self.history.get(symbol, [])

        if not h:
            return {"price": 0}

        price = h[-1]

        # 🔥 FIX: vždy vrací plný feature set
        if len(h) < 10:
            return {
                "price": price,
                "r1": 0, "r3": 0, "r5": 0,
                "ema_fast": price, "ema_mid": price, "ema_slow": price,
                "trend_strength": 0,
                "vol_5": 0, "vol_10": 0,
                "momentum": 0,
                "market_regime": "RANGE"
            }

        r1 = self._returns(h, 1)
        r3 = self._returns(h, 3)
        r5 = self._returns(h, 5)

        ema_fast = self._ema(h, 5)
        ema_mid = self._ema(h, 10)
        ema_slow = self._ema(h, 20)

        trend_strength = (ema_fast - ema_slow) / price

        vol_5 = self._std(h, 5) / price
        vol_10 = self._std(h, 10) / price

        momentum = r3 + r5

        # 🔥 REAL REGIME
        if trend_strength > 0.002:
            regime = "BULL"
        elif trend_strength < -0.002:
            regime = "BEAR"
        elif vol_10 < 0.0015:
            regime = "RANGE"
        else:
            regime = "VOLATILE"

        return {
            "price": price,
            "r1": r1, "r3": r3, "r5": r5,
            "ema_fast": ema_fast,
            "ema_mid": ema_mid,
            "ema_slow": ema_slow,
            "trend_strength": trend_strength,
            "vol_5": vol_5,
            "vol_10": vol_10,
            "momentum": momentum,
            "market_regime": regime
        }