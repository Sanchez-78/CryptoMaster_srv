class PortfolioManager:
    def __init__(self):
        self.balance = 1000
        self.open_trades = []
        self.trade_history = []

    def open_trade(self, symbol, action, price, confidence):
        trade = {
            "symbol": symbol,
            "action": action,
            "entry": price,
            "size": 50,
            "confidence": confidence,
        }
        self.open_trades.append(trade)
        print(f"📥 OPEN {symbol} {action}")
        return trade, "OPENED"

    def close_trade(self, trade, price):
        entry = trade["entry"]

        if trade["action"] == "BUY":
            profit = (price - entry) / entry
        else:
            profit = (entry - price) / entry

        result = "WIN" if profit > 0 else "LOSS"

        trade["profit"] = profit
        trade["result"] = result

        self.trade_history.append(trade)
        self.open_trades.remove(trade)

        print(f"📤 CLOSE {trade['symbol']} {result} {round(profit,5)}")

        return profit, result

    def update_trades(self, prices):
        closed = []

        for trade in list(self.open_trades):
            price = prices.get(trade["symbol"])
            if not price:
                continue

            entry = trade["entry"]

            if trade["action"] == "BUY":
                change = (price - entry) / entry
            else:
                change = (entry - price) / entry

            # 🔥 FIX: agresivní close (aby se učil)
            if abs(change) > 0.001:
                closed.append((trade, *self.close_trade(trade, price)))

        return closed

    def print_status(self):
        print(f"💼 Balance: {self.balance}")
        print(f"Open trades: {len(self.open_trades)}")
        print(f"Closed: {len(self.trade_history)}")