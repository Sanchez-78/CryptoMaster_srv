import time
import traceback
from datetime import datetime

from src.services.firebase_client import init_firebase, save_signal, load_all_signals, load_open_signals
from src.services.market_data import get_candles
from src.services.feature_extractor import extract_multi_tf_features
from src.services.meta_agent import MetaAgent
from src.services.evaluator import evaluate_signals

symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT"]

meta_agent = MetaAgent()


def run_pipeline():
    print("\n=== START PIPELINE ===")

    try:
        all_signals = load_all_signals()
        print(f"📂 Loaded all signals: {len(all_signals)}")

        for symbol in symbols:
            print(f"\n🔍 {symbol}")

            try:
                candles_m15 = get_candles(symbol, "15m")
                candles_h1 = get_candles(symbol, "1h")
                candles_h4 = get_candles(symbol, "4h")

                features = extract_multi_tf_features(
                    candles_m15,
                    candles_h1,
                    candles_h4
                )

                # ❗ SKIP pokud nejsou data
                if not features:
                    print("⚠️ Skipping - no features")
                    continue

                print("DEBUG FEATURES:", features)

                action, confidence = meta_agent.decide(features)

                print(f"🤖 FINAL: {action} ({confidence})")

                price = features.get("price", 0)

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

        # ✅ FIX evaluator
        print("\n🧪 Running evaluation...")
        for symbol in symbols:
            evaluate_signals(symbol)

        print("\n=== END PIPELINE ===")

    except Exception as e:
        print("❌ PIPELINE ERROR:", e)
        traceback.print_exc()


if __name__ == "__main__":
    print("🔥 BOT STARTED")
    init_firebase()

    while True:
        run_pipeline()
        time.sleep(300)