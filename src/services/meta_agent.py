class MetaAgent:
    def __init__(self):
        self.bias = 0.0
        self.patterns = {}

        # 📊 statistiky pro UI
        self.last_stats = {
            "winrate": 0.5,
            "avg_profit": 0.0,
            "patterns": 0,
        }

        self.total_trades = 0
        self.wins = 0

    # ─────────────────────────────
    # 🎯 DECISION ENGINE
    # ─────────────────────────────
    def decide(self, f):
        trend = f.get("trend_strength", 0)
        regime = f.get("market_regime", "RANGE")

        if trend > 0.002:
            action = "BUY"
            conf = 0.6
        elif trend < -0.002:
            action = "SELL"
            conf = 0.6
        else:
            return "HOLD", 0.2

        # 🔥 regime bonus
        if regime == "BULL":
            conf += 0.1
        elif regime == "BEAR":
            conf += 0.1

        # 🔥 pattern bonus
        key = f"{regime}_{round(trend,2)}_{action}"
        if key in self.patterns:
            conf += self.patterns[key]

        # 🔥 bias
        conf += self.bias
        conf = max(0, min(conf, 1))

        return action, conf

    # ─────────────────────────────
    # ⚡ EVENT-DRIVEN LEARNING
    # ─────────────────────────────
    def learn_from_trade(self, trade):
        profit = trade.get("profit", 0)
        result = trade.get("result", "LOSS")

        self.total_trades += 1

        if result == "WIN":
            self.wins += 1
            self.bias += 0.01
        else:
            self.bias -= 0.01

        # clamp bias
        self.bias = max(-0.5, min(self.bias, 0.5))

        # 🔥 pattern learning
        f = trade.get("features", {})
        regime = f.get("market_regime", "R")
        trend = round(f.get("trend_strength", 0), 2)
        action = trade.get("signal")

        key = f"{regime}_{trend}_{action}"

        if key not in self.patterns:
            self.patterns[key] = 0

        self.patterns[key] += profit
        self.patterns[key] = max(-1, min(self.patterns[key], 1))

        # 📊 stats (EMA styl)
        winrate = self.wins / max(self.total_trades, 1)

        self.last_stats["winrate"] = (
            self.last_stats["winrate"] * 0.99 + winrate * 0.01
        )

        self.last_stats["avg_profit"] = (
            self.last_stats["avg_profit"] * 0.99 + profit * 0.01
        )

        self.last_stats["patterns"] = len(self.patterns)

    # ─────────────────────────────
    # 🧠 FALLBACK: RAW LEARNING
    # ─────────────────────────────
    def learn_from_history(self, trades):
        if not trades:
            return

        wins = [t for t in trades if t.get("result") == "WIN"]
        total = len(trades)

        if total == 0:
            return

        winrate = len(wins) / total
        avg_profit = sum(t.get("profit", 0) for t in trades) / total

        self.bias += (winrate - 0.5) * 0.1

        self.last_stats["winrate"] = winrate
        self.last_stats["avg_profit"] = avg_profit
        self.last_stats["patterns"] = len(self.patterns)

    # ─────────────────────────────
    # 🧠 FALLBACK: COMPRESSED LEARNING
    # ─────────────────────────────
    def learn_from_compressed(self, trades):
        if not trades:
            return

        for t in trades:
            f = t.get("f", {})
            action = t.get("signal")
            profit = t.get("profit", 0)

            key = f"{f.get('r')}_{round(f.get('t',0),2)}_{action}"

            if key not in self.patterns:
                self.patterns[key] = 0

            self.patterns[key] += profit
            self.patterns[key] = max(-1, min(self.patterns[key], 1))

    # ─────────────────────────────
    # 📊 PROGRESS
    # ─────────────────────────────
    def get_progress(self):
        score = int(self.last_stats["winrate"] * 100)

        return {
            "score": score,
            "winrate": round(self.last_stats["winrate"], 3),
            "avg_profit": round(self.last_stats["avg_profit"], 5),
            "patterns": len(self.patterns),
            "bias": round(self.bias, 3),
            "trades": self.total_trades,
        }