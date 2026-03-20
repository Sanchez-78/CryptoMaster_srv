import random


class MetaAgent:
    def __init__(self):
        print("🧠 MetaAgent ready (simple mode)")

    def decide(self, features):
        price = features.get("price", 0)

        if not price:
            return "HOLD", 0.0

        # 🔥