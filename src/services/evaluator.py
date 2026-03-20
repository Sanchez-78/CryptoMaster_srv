from datetime import datetime, UTC, timedelta

from google.cloud.firestore_v1.base_query import FieldFilter

from src.services.firebase_client import db, update_signal
from src.services.learning import update_model_weights
from src.services.binance_client import fetch_candles
from src.services.firebase_client import get_db

db = get_db()
if db is None:
    return


EVAL_DELAY_HOURS = 1


# =========================
# 🧠 NORMALIZE TIMESTAMP
# =========================
def normalize_timestamp(ts):
    if ts is None:
        return None

    # string → datetime
    if isinstance(ts, str):
        try:
            return datetime.fromisoformat(ts).replace(tzinfo=UTC)
        except Exception:
            return None

    # Firestore timestamp → datetime
    try:
        return ts.replace(tzinfo=UTC)
    except Exception:
        return None


# =========================
# 🧪 EVALUATE SIGNALS
# =========================
def evaluate_signals(symbol, timeframe="1h"):
    print(f"\n🧪 Running evaluation for {symbol}...")

    try:
        cutoff = datetime.now(UTC) - timedelta(hours=EVAL_DELAY_HOURS)

        query = (
            db.collection("signals")
            .where(filter=FieldFilter("symbol", "==", symbol))
            .where(filter=FieldFilter("evaluated", "==", False))
        )

        docs = list(query.stream())

        print(f"🔎 Found {len(docs)} signals")

        for doc in docs:
            data = doc.to_dict()
            doc_id = doc.id

            try:
                # =========================
                # ⏱️ TIMESTAMP FIX
                # =========================
                timestamp = normalize_timestamp(data.get("timestamp"))

                if not timestamp or timestamp > cutoff:
                    continue

                entry_price = data.get("price")
                signal = data.get("signal")

                if not entry_price or not signal:
                    continue

                # =========================
                # 📈 LIVE PRICE
                # =========================
                candles = fetch_candles(symbol, "15m")

                if candles:
                    current_price = candles[-1]["close"]
                else:
                    current_price = entry_price

                # =========================
                # 💰 PROFIT (SAFE)
                # =========================
                profit = 0.0

                if signal == "BUY":
                    profit = (current_price - entry_price) / entry_price

                elif signal == "SELL":
                    profit = (entry_price - current_price) / entry_price

                # HOLD → 0

                result = "WIN" if profit > 0 else "LOSS"

                print(f"{signal} → {result} | 💰 {round(profit, 4)}")

                # =========================
                # 💾 UPDATE SIGNAL
                # =========================
                update_signal(doc_id, {
                    "evaluated": True,
                    "profit": profit,
                    "result": result,
                    "evaluated_at": datetime.now(UTC).isoformat()
                })

                # =========================
                # 🧠 LEARNING
                # =========================
                update_model_weights(data.get("features", {}), profit)

            except Exception as e:
                print("❌ Eval error:", e)

    except Exception as e:
        print("❌ Load signals error:", e)