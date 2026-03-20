class ProfitOptimizer:

    def __init__(self):
        self.min_confidence = 0.6
        self.max_trades = 5
        self.min_expected_move = 0.002  # 0.2%

    # =========================
    # 🚫 BLOCK LOGIC
    # =========================
    def block(self, signal, confidence, features=None, open_signals=None):
        if signal == "HOLD":
            return True

        if confidence < self.min_confidence:
            print("🚫 Low confidence")
            return True

        # =========================
        # 📉 TREND FILTER
        # =========================
        if features:
            trend = features.get("trend")

            if trend == "BULL" and signal == "SELL":
                print("🚫 Against trend")
                return True

            if trend == "BEAR" and signal == "BUY":
                print("🚫 Against trend")
                return True

            # =========================
            # 💰 MIN MOVE FILTER
            # =========================
            atr = features.get("atr_m15", 0)

            if atr < self.min_expected_move:
                print("🚫 Move too small (fees kill profit)")
                return True

        if open_signals and len(open_signals) >= self.max_trades:
            print("🚫 Too many trades")
            return True

        return False