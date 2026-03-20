import random


class MetaAgent:
    def __init__(self):
        print("🧠 MetaAgent ready (simple mode)")

    def decide(self, features):
        try:
            price = features.get("price", 0)
            change = features.get("change", 0)
            trend = features.get("trend", 0)
            volatility = features.get("volatility", 0)

            # ❌ ochrana
            if not price:
                return "HOLD", 0.0

            # 🔥 jednoduchá logika (ale funkční)
            if trend == 1 and change > 0:
                action = "BUY"
                confidence = min(0.5 + abs(change) * 5, 0.95)

            elif trend == -1 and change < 0:
                action = "SELL"
                confidence = min(0.5 + abs(change) * 5, 0.95)

            else:
                action = "HOLD"
                confidence = 0.4

            # 🔥 volatility boost
            if volatility == 1:
                confidence += 0.05

            confidence = max(0.0, min(confidence, 1.0))

            return action, confidence

        except Exception as e:
            print("❌ MetaAgent error:", e)
            return "HOLD", 0.0