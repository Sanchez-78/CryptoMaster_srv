class PortfolioManager:
    def __init__(self):
        self.balance = 1000.0  # USD
        self.max_risk_per_trade = 0.02  # 2%
        self.max_open_trades = 5

        self.open_trades = []
        self.trade_history = []

        self.win_streak = 0
        self.loss_streak = 0

        print("💼 PortfolioManager ready")

    # ---------------- POSITION SIZE ----------------
    def calculate_position_size(self, confidence):
        risk = self.balance * self.max_risk_per_trade

        # confidence scaling
        size = risk * (0.5 + confidence)

        return max(10, size)  # minimum trade

    # ---------------- CAN OPEN TRADE ----------------
    def can_open_trade(self):
        if len(self.open_trades) >= self.max_open_trades:
            return False, "MAX_TRADES"

        if self.loss_streak >= 5:
            return False, "LOSS_STREAK"

        return True, "OK"

    # ---------------- OPEN TRADE ----------------
    def open_trade(self, symbol, action, price, confidence):
        allowed, reason = self.can_open_trade()

        if not allowed:
            return None, reason

        size = self.calculate_position_size(confidence)

        trade = {
            "symbol": symbol,
            "action": action,
            "entry": price,
            "size": size,
            "confidence": confidence,
        }

        self.open_trades.append(trade)

        print(f"📥 OPEN {symbol} {action} | size={round(size,2)}")

        return trade, "OPENED"

    # ---------------- CLOSE TRADE ----------------
    def close_trade(self, trade, exit_price):
        entry = trade["entry"]
        size = trade["size"]
        action = trade["action"]

        if action == "BUY":
            profit = (exit_price - entry) / entry * size
        else:
            profit = (entry - exit_price) / entry * size

        self.balance += profit

        result = "WIN" if profit > 0 else "LOSS"

        if result == "WIN":
            self.win_streak += 1
            self.loss_streak = 0
        else:
            self.loss_streak += 1
            self.win_streak = 0

        trade["profit_usd"] = profit
        trade["result"] = result

        self.trade_history.append(trade)
        self.open_trades.remove(trade)

        print(
            f"📤 CLOSE {trade['symbol']} | {result} | "
            f"profit={round(profit,2)} | balance={round(self.balance,2)}"
        )

        return profit, result

    # ---------------- UPDATE OPEN TRADES ----------------
    def update_trades(self, price_map):
        closed = []

        for trade in list(self.open_trades):
            symbol = trade["symbol"]
            current_price = price_map.get(symbol)

            if not current_price:
                continue

            # 🔥 jednoduchý TP/SL
            entry = trade["entry"]

            if trade["action"] == "BUY":
                change = (current_price - entry) / entry
            else:
                change = (entry - current_price) / entry

            # TP / SL thresholds
            if change > 0.003 or change < -0.002:
                profit, result = self.close_trade(trade, current_price)
                closed.append((trade, profit, result))

        return closed

    # ---------------- SUMMARY ----------------
    def get_stats(self):
        total = len(self.trade_history)
        wins = len([t for t in self.trade_history if t["result"] == "WIN"])
        losses = len([t for t in self.trade_history if t["result"] == "LOSS"])

        winrate = wins / total if total else 0

        total_profit = sum(t.get("profit_usd", 0) for t in self.trade_history)

        return {
            "balance": round(self.balance, 2),
            "open_trades": len(self.open_trades),
            "total_trades": total,
            "winrate": round(winrate, 3),
            "profit_usd": round(total_profit, 2),
            "win_streak": self.win_streak,
            "loss_streak": self.loss_streak,
        }

    # ---------------- DEBUG PRINT ----------------
    def print_status(self):
        stats = self.get_stats()

        print("\n💼 PORTFOLIO:")
        print(f"Balance: {stats['balance']} USD")
        print(f"Open trades: {stats['open_trades']}")
        print(f"Total trades: {stats['total_trades']}")
        print(f"Winrate: {stats['winrate']}")
        print(f"Profit: {stats['profit_usd']} USD")
        print(f"🔥 Win streak: {stats['win_streak']}")
        print(f"💀 Loss streak: {stats['loss_streak']}")