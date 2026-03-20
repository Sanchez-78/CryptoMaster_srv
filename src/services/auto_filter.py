from src.services.firebase_client import db


# =========================
# 🧠 HELPERS
# =========================

def get_bucket(confidence):
    if confidence < 0.4:
        return "low"
    elif confidence < 0.7:
        return "mid"
    return "high"


def make_key(signal, trend, confidence):
    return f"{signal}_{trend}_{get_bucket(confidence)}"


# =========================
# 🔥 AUTO FILTER V2
# =========================

class AutoFilter:

    MIN_TRADES = 5
    MIN_WINRATE = 0.4
    MIN_PROFIT = -0.02  # tolerujeme malé ztráty

    def __init__(self):
        self.cache = {}

    # =========================
    # 📥 LOAD
    # =========================

    def load_stats(self, key):
        if key in self.cache:
            return self.cache[key]

        doc = db.collection("filter_stats").document(key).get()

        if doc.exists:
            data = doc.to_dict()
        else:
            data = {
                "wins": 0,
                "losses": 0,
                "total_profit": 0,
                "trades": 0
            }

        self.cache[key] = data
        return data

    # =========================
    # 💾 SAVE
    # =========================

    def save_stats(self, key, data):
        db.collection("filter_stats").document(key).set(data)
        self.cache[key] = data

    # =========================
    # 🔄 UPDATE (z evaluatoru)
    # =========================

    def update(self, signal, trend, confidence, profit):
        key = make_key(signal, trend, confidence)

        data = self.load_stats(key)

        data["trades"] += 1
        data["total_profit"] += profit

        if profit > 0:
            data["wins"] += 1
        else:
            data["losses"] += 1

        self.save_stats(key, data)

    # =========================
    # 🚫 FILTER LOGIC
    # =========================

    def allow(self, signal, trend, confidence):
        key = make_key(signal, trend, confidence)

        data = self.load_stats(key)

        trades = data["trades"]

        if trades < self.MIN_TRADES:
            print(f"🧪 Not enough data for {key}")
            return True

        winrate = data["wins"] / trades
        avg_profit = data["total_profit"] / trades

        print(f"🔎 Filter {key} → WR: {round(winrate,2)} | P: {round(avg_profit,3)}")

        if winrate < self.MIN_WINRATE:
            return False

        if avg_profit < self.MIN_PROFIT:
            return False

        return True