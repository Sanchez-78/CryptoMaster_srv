import time
import os
import json
import traceback
from datetime import datetime

# SERVICES
from src.services.feature_extractor import extract_multi_tf_features
from src.services.meta_agent import MetaAgent
from src.services.portfolio_manager import PortfolioManager
from src.services.profit_optimizer import ProfitOptimizer
from src.services.stabilizer import Stabilizer
from src.services.firebase_client import (
    init_firebase,
    save_signal,
    load_open_signals,
    load_all_signals,
    update_signal
)
from src.services.evaluator import evaluate_signals
from src.services.market_data import get_candles

# -------------------------------
# INIT
# -------------------------------

init_firebase()

meta_agent = MetaAgent()
portfolio = PortfolioManager()
optimizer = ProfitOptimizer()
stabilizer = Stabilizer()

SYMBOLS = ["BTCUSDT", "ETHUSDT", "ADAUSDT"]

# -------------------------------
# CORE PIPELINE
# -------------------------------

def run_pipeline():
    print("\n=== START PIPELINE ===")

    try:
        all_signals = load_all_signals()
        print(f"📂 Loaded all signals: {len(all_signals)}")

        for symbol in SYMBOLS:
            print(f"\n🔍 {symbol}")

            try:
                # -------------------------------
                # MARKET DATA
                # -------------------------------
                candles_m15 = get_candles(symbol, "15m")
                candles_h1 = get_candles(symbol, "1h")
                candles_h4 = get_candles(symbol, "4h")

                # -------------------------------
                # FEATURES
                # -------------------------------
                features = extract_multi_tf_features(
                    candles_m15,
                    candles_h1,
                    candles_h4
                )

                print(f"DEBUG FEATURES: {features}")

                # -------------------------------
                # AI DECISION
                # -------------------------------
                action, confidence = meta_agent.decide(features)

                print(f"🤖 FINAL: {action} ({confidence})")

                # -------------------------------
                # STABILIZER
                # -------------------------------
                if not stabilizer.allow_trade(action, confidence, all_signals):
                    print("🚫 Blocked by stabilizer")
                    continue

                # -------------------------------
                # OPTIMIZER
                # -------------------------------
                if not optimizer.allow_trade(action, confidence, features):
                    print("🚫 Blocked by optimizer")
                    continue

                # -------------------------------
                # PORTFOLIO CHECK
                # -------------------------------
                open_signals = load_open_signals()

                if not portfolio.can_open_trade(open_signals):
                    print("🚫 Portfolio limit reached")
                    continue

                # -------------------------------
                # EXECUTE (paper trade)
                # -------------------------------
                price = features.get("price", 0)
                size = portfolio.calculate_position_size(confidence)

                print("\n🚀 EXECUTING TRADE")
                print(f"{symbol} {action} size={size}")

                signal = {
                    "symbol": symbol,
                    "signal": action,
                    "confidence": float(confidence),
                    "price": float(price),
                    "features": features,
                    "result": None,
                    "profit": None,
                    "timestamp": datetime.utcnow().isoformat(),
                    "evaluated": False
                }

                save_signal(signal)
                print("💾 Signal saved")

            except Exception as e:
                print(f"❌ {symbol} error:", e)
                traceback.print_exc()

        # -------------------------------
        # EVALUATION
        # -------------------------------
        print("\n🧪 Running evaluation...")
        evaluate_signals()

        # -------------------------------
        # LEARNING
        # -------------------------------
        updated_signals = load_all_signals()
        meta_agent.learn(updated_signals)

        print("\n=== END PIPELINE ===")

    except Exception as e:
        print("❌ PIPELINE ERROR:", e)
        traceback.print_exc()


# -------------------------------
# LOOP (RAILWAY READY)
# -------------------------------

if __name__ == "__main__":
    print("🔥 BOT STARTED")

    while True:
        try:
            run_pipeline()
            time.sleep(300)  # 5 minut
        except Exception as e:
            print("❌ CRASH:", e)
            traceback.print_exc()
            time.sleep(60)