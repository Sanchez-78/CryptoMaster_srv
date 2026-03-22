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
from src.services.feature_engine import FeatureEngine

# ─── KONFIG ────────────────────────────────────────────────────────────────
SYMBOLS = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "SOLUSDT", "XRPUSDT"]
LOOP_DELAY = 10

agent = MetaAgent()
trade_filter = TradeFilter()
portfolio = PortfolioManager()
feature_engine = FeatureEngine()


# ─── PROGRESS RENDER ───────────────────────────────────────────────────────
def render_progress(progress):
    print("\n📊 PROGRESS:")

    print(f"winrate: {progress['winrate']}")
    print(f"avg_profit: {progress['avg_profit']}")
    print(f"patterns: {progress['patterns']}")
    print(f"bias: {progress['bias']}")

    score = progress["score"]
    filled = int(score / 5)
    bar = "█" * filled + "-" * (20 - filled)

    if score < 30:
        color = "\033[91m"
        emoji = "🔴"
    elif score < 60:
        color = "\033[93m"
        emoji = "🟡"
    else:
        color = "\033[92m"
        emoji = "🟢"

    print(f"{emoji} {color}[{bar}] {score}%\033[0m")


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
        })

    # ─── 2. GENERATE NEW TRADES ───────────────
    for symbol in SYMBOLS:
        try:
            price = prices.get(symbol)
            if not price:
                continue

            # 🔥 FEATURE ENGINE (KEY UPGRADE)
            feature_engine.update(symbol, price)
            features = feature_engine.build(symbol)

            # 🔥 DEBUG BONUS (vidíš trh)
            print(
                f"{symbol} | regime={features.get('market_regime')} "
                f"| trend={round(features.get('trend_strength',0),5)} "
                f"| vol={round(features.get('vol_10',0),5)}"
            )

            action, confidence = agent.decide(features)

            trade, status = portfolio.open_trade(symbol, action, price, confidence)

            if trade:
                trade["features"] = features

                print(
                    f"📥 {symbol} {action} | conf={round(confidence,2)}"
                )

        except Exception as e:
            print(f"❌ {symbol}:", e)
            traceback.print_exc()

    # ─── 3. LEARNING ───────────────────────────
    trades = load_recent_trades(1000)

    print(f"\n📦 Trades: {len(trades)}")
    print(f"🧠 Patterns: {len(agent.patterns)}")

    agent.learn_from_history(trades)

    # ─── 4. PROGRESS (STATE-DRIVEN) ────────────
    progress = agent.get_progress()
    render_progress(progress)

    # ─── 5. SAVE META ──────────────────────────
    save_meta_state({
        "progress": progress,
        "balance": portfolio.balance,
        "patterns": len(agent.patterns),
        "updated_at": datetime.now(UTC).isoformat(timespec="seconds"),
    })

    # ─── 6. PORTFOLIO DEBUG ────────────────────
    portfolio.print_status()

    print("=============================\n")


# ─── MAIN LOOP ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("🔥 BOT STARTED (FEATURE ENGINE + AI + PORTFOLIO)")

    while True:
        try:
            run_pipeline()
        except Exception as e:
            print("❌ PIPELINE ERROR:", e)
            traceback.print_exc()

        time.sleep(LOOP_DELAY)