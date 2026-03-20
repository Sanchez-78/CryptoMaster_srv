class MetaAgent:
    def __init__(self):
        self.bias = 0.0
        print("🧠 MetaAgent ready (learning enabled)")

    # ---------------- DECISION ----------------
    def decide(self, features):
        try:
            price = features.get("price", 0)
            change = features.get("change", 0)
            trend = features.get("trend", 0)
            volatility = features.get("volatility", 0)

            if not price:
                return "HOLD", 0.0

            # 🔥 základ logika
            if trend == 1 and change > 0:
                action = "BUY"
                confidence = min(0.5 + abs(change) * 5, 0.95)

            elif trend == -1 and change < 0:
                action = "SELL"
                confidence = min(0.5 + abs(change) * 5, 0.95)

            else:
                action = "HOLD"
                confidence = 0.3  # 🔥 sníženo

            # 🔥 volatility boost
            if volatility == 1:
                confidence += 0.05

            # 🔥 penalizace HOLD
            if action == "HOLD":
                confidence -= 0.1

            # 🔥 learning bias
            confidence += self.bias

            confidence = max(0.0, min(confidence, 1.0))

            return action, confidence

        except Exception as e:
            print("❌ MetaAgent error:", e)
            return "HOLD", 0.0

    # ---------------- LEARNING ----------------
    def learn_from_history(self, trades):
        if not trades:
            return

        wins = [t for t in trades if t.get("result") == "WIN"]
        losses = [t for t in trades if t.get("result") == "LOSS"]

        total = len(wins) + len(losses)
        if total == 0:
            return

        winrate = len(wins) / total

        # 🔥 AVG PROFIT
        profits = [t.get("profit", 0) for t in trades if t.get("profit") is not None]
        avg_profit = sum(profits) / len(profits) if profits else 0

        # 🔥 STRONG LEARNING
        self.bias = (winrate - 0.5) * 0.5
        self.bias += avg_profit * 2

        # clamp
        self.bias = max(-0.3, min(self.bias, 0.3))

        print(f"🧠 Learning | winrate={round(winrate,2)} bias={round(self.bias,3)}")