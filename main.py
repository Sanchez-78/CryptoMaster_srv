import time
import traceback
from datetime import datetime

from src.services.firebase_client import (
    init_firebase,
    save_signal,
    load_all_signals,
    load_open_signals
)

from src.services.market_data import get_all_prices
from src.services.meta_agent import MetaAgent
from src.services.evaluator import evaluate_signals


symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT"]
meta_agent = MetaAgent()

LEARNING_ONLY = True
MAX_DAILY_DRAWDOWN = -0.05

last_prices = {}
kill_switch_active_until = 0


def build_features(symbol, price):
    prev_price = last_prices.get(symbol)

    change = 0 if not prev_price else (price - prev_price) / prev_price

    trend = 1 if change > 0 else -1
    volatility = 1 if abs(change) > 0.01 else 0

    last_prices[symbol] = price

    return {
        "price": price,
        "change": change,
        "trend": trend,
        "volatility": volatility
    }


def check_kill_switch(signals):
    global kill_switch_active_until

    if time.time() < kill_switch_active_until:
        return True

    recent = [
        s for s in signals
        if s.get("evaluated") and s.get("profit") is not None
    ][-20:]

    if len(recent) < 10:
        return False

    total = sum(s["profit"] for s in recent)

    if total < -0.05:
        kill_switch_active_until = time.time() + 3600
        print(f"🛑 KILL SWITCH ACTIVE | pnl={round(total,4)}")
        return True

    return False


def run_pipeline():
    print("\n=== START PIPELINE ===")

    init_firebase()

    try:
        all_signals = load_all_signals()
        kill = check_kill_switch(all_signals)

        prices = get_all_prices()
        if not prices:
            print("❌ No prices")
            return

        for symbol in symbols:
            try:
                price = prices.get(symbol)
                if not price:
                    continue

                features = build_features(symbol, price)

                # 🔥 SAFE CALL
                result = meta_agent.decide(features)

                if not result or not isinstance(result, tuple):
                    print("⚠️ MetaAgent invalid:", result)
                    action, confidence = "HOLD", 0.0
                else:
                    action, confidence = result

                print(f"{symbol} | {action} | {confidence:.2f}")

                signal = {
                    "symbol": symbol,
                    "signal": action,
                    "confidence": float(confidence),
                    "price": float(price),
                    "features": features,
                    "result": None,
                    "profit": None,
                    "age": 0,
                    "timestamp": datetime.utcnow().isoformat(),
                    "evaluated": False,
                    "mode": "learning"
                }

                # 🔥 LEARNING ONLY
                if LEARNING_ONLY:
                    save_signal(signal)
                    continue

                # trading vypnutý pokud kill switch
                if kill:
                    continue

            except Exception as e:
                print(f"❌ {symbol} error:", e)
                traceback.print_exc()

        print("\n🧪 Evaluating...")

        for symbol in symbols:
            evaluate_signals(symbol)

    except Exception as e:
        print("❌ PIPELINE ERROR:", e)
        traceback.print_exc()


if __name__ == "__main__":
    print("🔥 BOT STARTED")

    while True:
        run_pipeline()
        time.sleep(60)