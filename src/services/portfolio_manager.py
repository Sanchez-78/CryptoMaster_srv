class PortfolioManager:

    def __init__(self):
        # =========================
        # ⚙️ CONFIG
        # =========================
        self.max_open_trades = 10
        self.bootstrap_mode = True  # 🔥 první fáze → sběr dat
        self.max_side_ratio = 0.7   # max 70% BUY/SELL

    # =========================
    # 📊 ANALYZE PORTFOLIO
    # =========================
    def analyze(self, open_signals):
        stats = {
            "total": len(open_signals),
            "BUY": 0,
            "SELL": 0
        }

        for s in open_signals:
            side = s.get("signal")

            if side == "BUY":
                stats["BUY"] += 1
            elif side == "SELL":
                stats["SELL"] += 1

        return stats

    # =========================
    # 🧠 CAN OPEN TRADE
    # =========================
    def can_open(self, signal, open_signals):
        stats = self.analyze(open_signals)

        # =========================
        # 🚀 BOOTSTRAP MODE
        # =========================
        if self.bootstrap_mode:
            print("🚀 Bootstrap mode → allowing trade")
            return True

        # =========================
        # 🚫 MAX TRADES
        # =========================
        if stats["total"] >= self.max_open_trades:
            print("🚫 Max open trades reached")
            return False

        # =========================
        # ⚖️ SIDE BALANCE
        # =========================
        if stats["total"] > 0:
            if signal == "BUY":
                ratio = stats["BUY"] / stats["total"]
                if ratio > self.max_side_ratio:
                    print("🚫 Too many BUY positions")
                    return False

            if signal == "SELL":
                ratio = stats["SELL"] / stats["total"]
                if ratio > self.max_side_ratio:
                    print("🚫 Too many SELL positions")
                    return False

        return True

    # =========================
    # 💰 POSITION SCALING
    # =========================
    def scale_size(self, base_size, open_signals):
        stats = self.analyze(open_signals)

        if stats["total"] == 0:
            return base_size

        # čím víc trade → menší size
        scale = 1 - (stats["total"] / self.max_open_trades)

        return base_size * max(scale, 0.3)

    # =========================
    # 📉 RISK REDUCTION
    # =========================
    def risk_adjustment(self, size, regime, volatility):
        # volatilita
        if volatility == "HIGH":
            size *= 0.5

        # regime
        if regime == "VOLATILE":
            size *= 0.5
        elif regime in ["BULL_TREND", "BEAR_TREND"]:
            size *= 1.2

        return size

    # =========================
    # 🎯 FINAL SIZE
    # =========================
    def compute_size(self, base_size, open_signals, regime, volatility):
        size = self.scale_size(base_size, open_signals)
        size = self.risk_adjustment(size, regime, volatility)

        return round(size, 4)