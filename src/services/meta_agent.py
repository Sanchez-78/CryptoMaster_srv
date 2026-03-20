from src.services.fx_service import get_usd_to_czk


class MetaAgent:
    def __init__(self):
        self.bias = 0.0
        self.patterns = {}

        self.usd_to_czk = 23.0  # fallback
        self.account_size = 1000  # USD (simulace kapitálu)

        self.last_stats = {
            "winrate": 0,
            "avg_profit": 0,
            "patterns": 0
        }

        print("🧠 MetaAgent ready (ultimate + fx + dashboard)")

    # ---------------- DECISION ----------------
    def decide(self, features):
        try:
            price = features.get("price", 0)
            if not price:
                return "HOLD", 0.0

            m15 = features.get("m15_trend", 0)
            h1 = features.get("h1_trend", 0)
            h4 = features.get("h4_trend", 0)

            m15_vol = features.get("m15_volatility", 0)
            h1_vol = features.get("h1_volatility", 0)
            h4_vol = features.get("h4_volatility", 0)

            trend_score = m15 + h1 + h4

            if trend_score >= 2:
                action = "BUY"
                confidence = 0.6
            elif trend_score <= -2:
                action = "SELL"
                confidence = 0.6
            else:
                action = "HOLD"
                confidence = 0.3

            vol_score = m15_vol + h1_vol + h4_vol
            confidence += vol_score * 0.05

            key = f"{trend_score}_{vol_score}_{action}"
            if key in self.patterns:
                confidence += self.patterns[key]

            if action == "HOLD":
                confidence -= 0.1

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

        # 🔥 LIVE FX
        self.usd_to_czk = get_usd_to_czk()

        wins = [t for t in trades if t.get("result") == "WIN"]
        losses = [t for t in trades if t.get("result") == "LOSS"]

        total = len(wins) + len(losses)
        if total == 0:
            return

        winrate = len(wins) / total

        profits = [t.get("profit", 0) for t in trades if t.get("profit") is not None]
        avg_profit = sum(profits) / len(profits) if profits else 0

        # 🔥 GLOBAL BIAS
        self.bias = (winrate - 0.5) * 0.6
        self.bias += avg_profit * 3
        self.bias = max(-0.4, min(self.bias, 0.4))

        # ---------------- PATTERN LEARNING ----------------
        for t in trades:
            features = t.get("features", {})
            action = t.get("signal")
            result = t.get("result")

            if not features or not action:
                continue

            if result not in ["WIN", "LOSS"]:
                continue

            m15 = features.get("m15_trend", 0)
            h1 = features.get("h1_trend", 0)
            h4 = features.get("h4_trend", 0)

            vol = (
                features.get("m15_volatility", 0)
                + features.get("h1_volatility", 0)
                + features.get("h4_volatility", 0)
            )

            trend_score = m15 + h1 + h4
            key = f"{trend_score}_{vol}_{action}"

            if key not in self.patterns:
                self.patterns[key] = 0.0

            # 🔥 SMART REWARD
            profit = t.get("profit", 0)
            confidence = t.get("confidence", 0.5)

            if action == "BUY":
                aligned = trend_score > 0
            elif action == "SELL":
                aligned = trend_score < 0
            else:
                aligned = False

            trend_bonus = 0.02 if aligned else -0.02
            vol_quality = 0.01 if vol >= 2 else -0.01
            conf_bonus = (confidence - 0.5) * 0.05

            reward = (
                profit * 3 +
                trend_bonus +
                vol_quality +
                conf_bonus
            )

            self.patterns[key] += reward
            self.patterns[key] = max(-0.5, min(self.patterns[key], 0.5))

        print(
            f"🧠 Learning | winrate={round(winrate,2)} "
            f"bias={round(self.bias,3)} "
            f"patterns={len(self.patterns)}"
        )

        self.print_progress(winrate, avg_profit)
        self.print_user_summary(trades)

    # ---------------- PROGRESS ----------------
    def print_progress(self, winrate, avg_profit):
        prev = self.last_stats

        def trend(new, old):
            if new > old:
                return "↑"
            elif new < old:
                return "↓"
            return "="

        score = (
            winrate * 50 +
            max(min(avg_profit * 1000, 25), -25) +
            min(len(self.patterns), 25)
        )

        score = max(0, min(int(score), 100))

        print("\n📊 PROGRESS:")
        print(f"winrate: {round(winrate,3)} {trend(winrate, prev['winrate'])}")
        print(f"avg_profit: {round(avg_profit,5)} {trend(avg_profit, prev['avg_profit'])}")
        print(f"patterns: {len(self.patterns)} {trend(len(self.patterns), prev['patterns'])}")
        print(f"bias: {round(self.bias,3)}")

        print(f"score: {self.color_score(score)}/100")
        print(self.progress_bar(score))

        self.last_stats = {
            "winrate": winrate,
            "avg_profit": avg_profit,
            "patterns": len(self.patterns)
        }

    # ---------------- USER DASHBOARD ----------------
    def print_user_summary(self, trades):
        wins = [t for t in trades if t.get("result") == "WIN"]
        losses = [t for t in trades if t.get("result") == "LOSS"]

        total = len(wins) + len(losses)
        if total == 0:
            return

        winrate = len(wins) / total

        profits = [t.get("profit", 0) for t in trades]
        total_profit = sum(profits)

        avg_win = sum([t.get("profit", 0) for t in wins]) / len(wins) if wins else 0
        avg_loss = sum([t.get("profit", 0) for t in losses]) / len(losses) if losses else 0

        # 🔥 CZK přepočet
        total_czk = total_profit * self.account_size * self.usd_to_czk
        avg_win_czk = avg_win * self.account_size * self.usd_to_czk
        avg_loss_czk = avg_loss * self.account_size * self.usd_to_czk

        # 🔥 streaky
        best_streak = 0
        worst_streak = 0
        cw = cl = 0

        for t in trades:
            if t.get("result") == "WIN":
                cw += 1
                cl = 0
            elif t.get("result") == "LOSS":
                cl += 1
                cw = 0

            best_streak = max(best_streak, cw)
            worst_streak = max(worst_streak, cl)

        # 🔥 status
        if winrate > 0.6:
            status = "VYDĚLÁVÁ 🟢"
        elif winrate > 0.45:
            status = "ZLEPŠUJE SE 🟡"
        else:
            status = "SLABÝ 🔴"

        print("\n🤖 STAV ROBOTA:")
        print(f"Celkem obchodů: {total}")
        print(f"Úspěšnost: {round(winrate * 100, 1)}%")
        print(f"Zisky: {len(wins)}")
        print(f"Ztráty: {len(losses)}")

        print(f"\n💰 Celkový profit: {round(total_profit,4)} (≈ {int(total_czk)} Kč)")
        print(f"📈 Průměrný zisk: {round(avg_win,4)} (≈ {int(avg_win_czk)} Kč)")
        print(f"📉 Průměrná ztráta: {round(avg_loss,4)} (≈ {int(avg_loss_czk)} Kč)")

        print(f"\n🔥 Nejlepší série: {best_streak}")
        print(f"💀 Nejhorší série: {worst_streak}")

        print(f"\n💱 USD/CZK: {round(self.usd_to_czk,2)}")
        print(f"📊 Stav: {status}")

    # ---------------- COLOR SCORE ----------------
    def color_score(self, score):
        if score < 30:
            return f"\033[91m{score}\033[0m"
        elif score < 50:
            return f"\033[93m{score}\033[0m"
        elif score < 70:
            return f"\033[94m{score}\033[0m"
        else:
            return f"\033[92m{score}\033[0m"

    # ---------------- PROGRESS BAR ----------------
    def progress_bar(self, score):
        total = 20
        filled = int(score / 100 * total)

        if score < 30:
            color = "\033[91m"
        elif score < 50:
            color = "\033[93m"
        elif score < 70:
            color = "\033[94m"
        else:
            color = "\033[92m"

        reset = "\033[0m"

        bar = ""
        for i in range(total):
            if i < filled:
                bar += f"{color}█{reset}"
            else:
                bar += "-"

        return f"[{bar}] {score}%"