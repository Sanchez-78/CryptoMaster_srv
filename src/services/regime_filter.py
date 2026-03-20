class RegimeFilter:

    def allow(self, signal, regime):
        # =========================
        # 🔓 DOČASNĚ POVOLENO
        # =========================
        if regime == "SIDEWAYS":
            return True

        if regime == "BULL_TREND":
            return signal == "BUY"

        if regime == "BEAR_TREND":
            return signal == "SELL"

        if regime == "VOLATILE":
            return True

        return True