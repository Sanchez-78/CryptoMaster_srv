import time
import random
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

# ─── KONFIG ────────────────────────────────────────────────────────────────
SYMBOLS = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "SOLUSDT", "XRPUSDT"]
LEARNING_MODE = True
LOOP_DELAY = 10  # 🔥 rychlejší learning

agent = MetaAgent()
trade_filter = TradeFilter()
last_prices = {}

# 🔥 MARKET TREND (klíčové pro learning)
market_bias = 0


# ─── SIMULACE (REALISTIČTĚJŠÍ) ─────────────────────────────────────────────
def simulate_trade(action: str, price: float) -> float:
    global market_bias

    # pomalu se měnící trend
    market_bias += random.uniform(-0.0005, 0.0005)
    market_bias = max(-0.003, min(0.003, market_bias))

    noise = random.uniform(-0.002, 0.002)
    future = price * (1 + market_bias + noise)

    if action == "BUY":
        return (future - price) / price
    elif action == "SELL":
        return (price - future) / price
    return 0.0


# ─── FEATURE ENGINE (REAL HISTORY) ─────────────────────────────────────────
def build_features(symbol: str, price: float) -> dict:
    prev = last_prices.get(symbol, {"history": []})
    history = prev.get("history", [])

    history.append(price)
    if len(history) > 20:
        history.pop(0)

    prev["history"] = history

    def trend(n):
        if len(history) < n:
            return 0
        return 1 if history[-1] > history[-n] else -1

    def volatility(n):
        if len(history) < n:
            return 0
        window = history[-n:]
        change = max(window) - min(window)
        return 1 if change / price > 0.003 else 0

    feats = {
        "price": price,

        "m15_trend": trend(3),
        "h1_trend": trend(6),
        "h4_trend": trend(12),

        "m15_volatility": volatility(3),
        "h1_volatility": volatility(6),
        "h4_volatility": volatility(12),
    }

    last_prices[symbol] = prev
    return feats


# ─── SAVE META ─────────────────────────────────────────────────────────────
def _save_meta(trades: list) -> None:
    try:
        wins = [t for t in trades if t.get("result") == "WIN"]
        losses = [t for t in trades if t.get("result") == "LOSS"]

        total = len(wins) + len(losses)
        if total == 0:
            return

        winrate = len(wins) / total

        profits = [t.get("profit", 0) for t in trades if t.get("profit") is not None]
        avg_profit = sum(profits) / len(profits) if profits else 0

        avg_win = sum(t.get("profit", 0) for t in wins) / len(wins) if wins else 0
        avg_loss = sum(t.get("profit", 0) for t in losses) / len(losses) if losses else 0

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
            "avg_profit": round(avg_profit, 5),
            "avg_win": round(avg_win, 5),
            "avg_loss": round(avg_loss, 5),
            "total_profit": round(sum(profits), 5),
            "patterns":   len(agent.patterns),
            "bias":       round(agent.bias, 4),
            "fx_usd_czk": round(agent.usd_to_czk, 2),
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

    for symbol in SYMBOLS:
        try:
            price = prices.get(symbol)
            if not price:
                continue

            features = build_features(symbol, price)
            action, confidence = agent.decide(features)

            if not LEARNING_MODE:
                allowed, reason = trade_filter.allow_trade(action, confidence, features)
                if not allowed:
                    print(f"{symbol} ❌ FILTERED: {reason}")
                    continue
                trade_filter.register_trade()

            profit = simulate_trade(action, price)
            result = "WIN" if profit > 0 else "LOSS"

            save_signal({
                "symbol": symbol,
                "signal": action,
                "confidence": float(confidence),
                "price": float(price),
                "features": features,
                "profit": float(profit),
                "result": result,
                "evaluated": True,
                "timestamp": datetime.now(UTC).isoformat(timespec="seconds"),
                "mode": "learning",
            })

            print(f"{symbol} {action} | conf={confidence:.2f} | profit={profit:.5f} | {result}")

        except Exception as e:
            print(f"❌ {symbol}:", e)
            traceback.print_exc()

    # 🔥 LOAD VÍCE DAT
    trades = load_recent_trades(1000)
    print(f"\n📦 Trades: {len(trades)}")
    print(f"🧠 Patterns: {len(agent.patterns)}")

    agent.learn_from_history(trades)
    _save_meta(trades)

    print("=============================\n")


# ─── MAIN LOOP ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("🔥 BOT STARTED (REAL LEARNING MODE)")

    while True:
        try:
            run_pipeline()
        except Exception as e:
            print("❌ PIPELINE ERROR:", e)
            traceback.print_exc()

        time.sleep(LOOP_DELAY)