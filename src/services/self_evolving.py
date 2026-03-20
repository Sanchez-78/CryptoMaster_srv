import random


class SelfEvolvingSystem:

    def __init__(self):
        self.params = {
            "risk_multiplier": 1.0,
            "confidence_boost": 1.0,
            "exploration": 0.3
        }

    # =========================
    # 🧠 EVOLVE
    # =========================
    def evolve(self, performance):
        winrate = performance.get("winrate", 0)
        profit = performance.get("profit", 0)

        print("🧬 Evolving with:", performance)

        # =========================
        # 📈 GOOD PERFORMANCE
        # =========================
        if winrate > 50 and profit > 0:
            self.params["risk_multiplier"] *= 1.05
            self.params["confidence_boost"] *= 1.02
            self.params["exploration"] *= 0.95

        # =========================
        # 📉 BAD PERFORMANCE
        # =========================
        else:
            self.params["risk_multiplier"] *= 0.9
            self.params["confidence_boost"] *= 0.95
            self.params["exploration"] *= 1.05

        # =========================
        # 🎲 MUTATION
        # =========================
        if random.random() < 0.1:
            key = random.choice(list(self.params.keys()))
            self.params[key] *= random.uniform(0.9, 1.1)
            print(f"🧬 Mutation on {key}")

        # clamp
        self.params["risk_multiplier"] = max(0.5, min(2.0, self.params["risk_multiplier"]))
        self.params["confidence_boost"] = max(0.5, min(2.0, self.params["confidence_boost"]))
        self.params["exploration"] = max(0.01, min(0.5, self.params["exploration"]))

        print("🧬 Params:", self.params)

        return self.params