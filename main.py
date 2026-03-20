from src.services.binance_client import get_price
from src.features.multi_tf import extract_multi_tf_features
from src.ai.meta_agent import MetaAgent
from src.storage.firebase import save_signal, load_recent_trades
from src.filters.signal_filter import filter_signal

import time
import random

# 🔥 FORCE LEARNING MODE
LEARNING_MODE = True

agent = MetaAgent()


# ---------------- SIMULACE ----------------
def simulate_trade(action, price):
    # fake future movement (pro learning)
    future_price = price * (1 + random.uniform(-0.003, 0.003))

    if action == "BUY":
        return (future_price - price) / price
    elif action == "SELL":
        return (price - future_price) / price
    return 0


# ---------------- MAIN LOOP ----------------
while True:
    try:
        symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT"]

        for symbol in symbols:
            price = get_price(symbol)

            features = extract_multi_tf_features(symbol)
            features["price"] = price

            action, confidence = agent.decide(features)

            # 🔥 FILTER (override in learning mode)
            filtered = filter_signal(symbol, action, confidence, features)

            if filtered is None and not LEARNING_MODE:
                print(f"{symbol} ❌ FILTERED")
                continue

            # 🔥 SIMULACE místo real trade
            profit = simulate_trade(action, price)

            result = "WIN" if profit > 0 else "LOSS"

            signal_data = {
                "symbol": symbol,
                "signal": action,
                "confidence": confidence,
                "price": price,
                "features": features,
                "profit": profit,
                "result": result,
                "timestamp": int(time.time()),
                "executed": False if LEARNING_MODE else True
            }

            # 🔥 vždy ukládej
            save_signal(signal_data)

            print(
                f"{symbol} {action} | conf={round(confidence,2)} "
                f"| profit={round(profit,5)} | {result}"
            )

        # 🔥 LOAD VÍC DAT
        trades = load_recent_trades(1000)

        print(f"\n📦 LOADED TRADES: {len(trades)}")

        # 🔥 LEARNING
        agent.learn_from_history(trades)

        print("\n=============================\n")

        time.sleep(5)

    except Exception as e:
        print("❌ MAIN ERROR:", e)
        time.sleep(5)