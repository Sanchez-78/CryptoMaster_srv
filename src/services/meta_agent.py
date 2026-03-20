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

            if trend == 1 and change > 0:
                action = "BUY"
                confidence = min(0.5 + abs(change) * 5, 0.95)

            elif trend == -1 and change < 0:
                action = "SELL"
                confidence = min(0.5 + abs(change) * 5, 0.95)

            else:
                action = "HOLD"
                confidence = 0.4

            if volatility == 1:
                confidence += 0.05

            # 🔥 LEARNING BIAS
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

        print(f"🧠 Learning | winrate={round(winrate,2)}")

        # 🔥 adaptace
        if winrate < 0.5:
            self.bias = -0.05
        else:
            self.bias = 0.05