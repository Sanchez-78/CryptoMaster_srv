import random


class AutoStrategy:

    def __init__(self):
        self.strategies = []

    # =========================
    # 🎲 GENERATE
    # =========================
    def generate(self):
        strat = {
            "rsi_low": random.uniform(0.2, 0.4),
            "rsi_high": random.uniform(0.6, 0.8),
            "macd_threshold": random.uniform(-0.01, 0.01)
        }

        self.strategies.append(strat)
        print("🧪 New strategy:", strat)

    # =========================
    # 🤖 APPLY
    # =========================
    def decide(self, features):
        if not self.strategies:
            return "HOLD", 0.3

        strat = random.choice(self.strategies)

        rsi = features.get("rsi_m15", 0)
        macd = features.get("macd_m15", 0)

        if rsi < strat["rsi_low"] and macd > strat["macd_threshold"]:
            return "BUY", 0.6

        if rsi > strat["rsi_high"] and macd < strat["macd_threshold"]:
            return "SELL", 0.6

        return "HOLD", 0.3

    # =========================
    # 🧠 FILTER
    # =========================
    def evolve(self, signals):
        if len(self.strategies) < 3:
            self.generate()