import time
import traceback
from datetime import datetime, UTC

from src.services.market_data import get_all_prices
from src.services.meta_agent import MetaAgent
from src.services.firebase_client import (
    init_firebase,
    save_signal,
    load_recent_trades,
    save_meta_state,
)
from src.services.trade_filter import TradeFilter
from src.services.portfolio_manager import PortfolioManager

# ─── KONFIG ────────────────────────────────────────────────────────────────
SYMBOLS = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "SOLUSDT", "XRPUSDT"]
LEARNING_MODE = True
LOOP_DELAY = 10

agent = MetaAgent()
trade_filter = TradeFilter()
portfolio = PortfolioManager()

# ─── META SAVE ─────────────────────────────────────────────────────────────
def _save_meta(trades: list):
    try:
        wins = [t for t in trades if t.get("result") == "WIN"]
        losses = [t for t in trades if t.get("result") == "LOSS"]

        total = len(wins) + len(losses)
        if total == 0:
            return

        winrate = len(wins) / total

        profits = [t.get("profit", 0) for t in trades]
        total_profit = sum(profits)
        avg_profit = total_profit / total if total else 0

        score = int(max(0, min(
            winrate * 50 +
            max(min(avg_profit * 1000, 25), -25) +
            min(len(agent.patterns), 25),
            100
        )))

        if winrate > 0.6:
            status = "VYDĚLÁVÁ 🟢"
        elif winrate > 0.45:
            status = "ZLEPŠUJE SE 🟡"
        else:
            status = "SLABÝ 🔴"

        save_meta_state({
            "score": score,
            "status": status,
            "winrate": round(winrate, 3),
            "total": total,
            "wins": len(wins),
            "losses": len(losses),
            "total_profit": round(total_profit, 5),
            "patterns": len(agent.patterns),
            "balance": portfolio.balance,
            "updated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        })

        print(f"📊 META | score={score} status={status}")

    except Exception as e:
        print("❌ META ERROR:", e)


# ─── PIPELINE ──────────────────────────────────────────────────────────────
def run_pipeline():
    print("\n=== PIPELINE ===")

    init_firebase()
    trade_filter.reset()

    prices = get_all_prices()
    if not prices:
        prices = {
            "BTCUSDT": 60000,
            "ETHUSDT": 3000,
            "ADAUSDT": 0.5,
            "SOLUSDT": 150,
            "XRPUSDT": 0.6,
        }

    # ─── 1. UPDATE OPEN TRADES ─────────────────
    closed_trades = portfolio.update_trades(prices)

    for trade, profit, result in closed_trades:
        save_signal({
            "symbol": trade["symbol"],
            "signal": trade["action"],
            "confidence": trade["confidence"],
            "features": trade.get("features", {}),
            "profit": profit,
            "result": result,
            "evaluated": True,
            "timestamp": datetime.now(UTC).isoformat(timespec="seconds"),
            "mode": "portfolio",
        })

    # ─── 2. GENERATE NEW SIGNALS ───────────────
    for symbol in SYMBOLS:
        try:
            price = prices.get(symbol)
            if not price:
                continue

            # 🔥 jednoduché features (bereš z tvého systému / můžeš napojit multiTF)
            features = {
                "price": price,
            }

            action, confidence = agent.decide(features)

            if not LEARNING_MODE:
                allowed, reason = trade_filter.allow_trade(action, confidence, features)
                if not allowed:
                    print(f"{symbol} ❌ FILTERED: {reason}")
                    continue
                trade_filter.register_trade()

            # 🔥 otevři trade
            trade, status = portfolio.open_trade(symbol, action, price, confidence)

            if trade:
                trade["features"] = features  # uložíme pro learning

        except Exception as e:
            print(f"❌ {symbol}:", e)
            traceback.print_exc()

    # ─── 3. LEARNING ───────────────────────────
    trades = load_recent_trades(1000)

    print(f"\n📦 Trades: {len(trades)}")
    print(f"🧠 Patterns: {len(agent.patterns)}")

    agent.learn_from_history(trades)

    # ─── 4. META + DEBUG ───────────────────────
    _save_meta(trades)
    portfolio.print_status()

    print("=============================\n")


# ─── MAIN LOOP ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("🔥 BOT STARTED (PORTFOLIO MODE)")

    while True:
        try:
            run_pipeline()
        except Exception as e:
            print("❌ PIPELINE ERROR:", e)
            traceback.print_exc()

        time.sleep(LOOP_DELAY)