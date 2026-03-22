import math


class FeatureEngine:
    def __init__(self):
        self.history = {}  # symbol -> price history

    # ---------------- UPDATE HISTORY ----------------
    def update(self, symbol: str, price: float):
        if symbol not in self.history:
            self.history[symbol] = []

        h = self.history[symbol]
        h.append(price)

        if len(h) > 100:
            h.pop(0)

    # ---------------- HELPERS ----------------
    def _returns(self, h, n):
        if len(h) < n + 1:
            return 0.0
        return (h[-1] - h[-n]) / h[-n]

    def _log_return(self, h):
        if len(h) < 2:
            return 0.0
        return math.log(h[-1] / h[-2])

    def _ema(self, h, period):
        if len(h) < period:
            return h[-1] if h else 0

        k = 2 / (period + 1)
        ema = h[-period]

        for price in h[-period:]:
            ema = price * k + ema * (1 - k)

        return ema

    def _std(self, h, n):
        if len(h) < n:
            return 0.0

        window = h[-n:]
        mean = sum(window) / n
        var = sum((x - mean) ** 2 for x in window) / n

        return math.sqrt(var)

    # ---------------- MAIN FEATURES ----------------
    def build(self, symbol: str) -> dict:
        h = self.history.get(symbol, [])

        if len(h) < 10:
            return {"price": h[-1] if h else 0}

        price = h[-1]

        # 🔥 RETURNS
        r1 = self._returns(h, 1)
        r3 = self._returns(h, 3)
        r5 = self._returns(h, 5)

        log_r = self._log_return(h)

        # 🔥 EMA TREND
        ema_fast = self._ema(h, 5)
        ema_mid = self._ema(h, 10)
        ema_slow = self._ema(h, 20)

        trend_strength = (ema_fast - ema_slow) / price

        # 🔥 VOLATILITY
        vol_5 = self._std(h, 5) / price
        vol_10 = self._std(h, 10) / price

        # 🔥 MOMENTUM
        momentum = r3 + r5

        # 🔥 DIRECTION FLAGS
        trend_dir = 1 if trend_strength > 0 else -1
        momentum_dir = 1 if momentum > 0 else -1

        # 🔥 REGIME DETECTION (REAL)
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

            # returns
            "r1": r1,
            "r3": r3,
            "r5": r5,
            "log_return": log_r,

            # trend
            "ema_fast": ema_fast,
            "ema_mid": ema_mid,
            "ema_slow": ema_slow,
            "trend_strength": trend_strength,
            "trend_dir": trend_dir,

            # volatility
            "vol_5": vol_5,
            "vol_10": vol_10,

            # momentum
            "momentum": momentum,
            "momentum_dir": momentum_dir,

            # regime
            "market_regime": regime,
        }