import os
import firebase_admin

from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter


# =========================
# 🔐 INIT FIREBASE
# =========================
def init_firebase():
    if not firebase_admin._apps:
        cred_path = os.path.join(os.getcwd(), "firebase_key.json")

        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)

        print("🔥 Firebase connected")

    return firestore.client()


db = init_firebase()


# =========================
# 💾 SAVE SIGNAL
# =========================
def save_signal(data):
    try:
        db.collection("signals").add(data)
        print("💾 Signal saved")
    except Exception as e:
        print("❌ Save signal error:", e)


# =========================
# 📥 LOAD OPEN SIGNALS
# =========================
def load_open_signals(limit=50):
    try:
        query = (
            db.collection("signals")
            .where(filter=FieldFilter("evaluated", "==", False))
            .limit(limit)
        )

        docs = query.stream()

        results = []
        for doc in docs:
            d = doc.to_dict()
            d["id"] = doc.id
            results.append(d)

        print(f"📂 Loaded open signals: {len(results)}")
        return results

    except Exception as e:
        print("❌ Load open signals error:", e)
        return []


# =========================
# 📥 LOAD ALL SIGNALS
# =========================
def load_all_signals(limit=500):
    try:
        docs = db.collection("signals").limit(limit).stream()

        results = []
        for doc in docs:
            d = doc.to_dict()
            d["id"] = doc.id
            results.append(d)

        print(f"📂 Loaded all signals: {len(results)}")
        return results

    except Exception as e:
        print("❌ Load all signals error:", e)
        return []


# =========================
# 📊 LOAD SIGNALS BY SYMBOL
# =========================
def load_signals_by_symbol(symbol, limit=100):
    try:
        query = (
            db.collection("signals")
            .where(filter=FieldFilter("symbol", "==", symbol))
            .limit(limit)
        )

        docs = query.stream()

        return [doc.to_dict() for doc in docs]

    except Exception as e:
        print("❌ Load symbol signals error:", e)
        return []


# =========================
# 🧠 LOAD WEIGHTS
# =========================
def load_weights():
    try:
        doc = db.collection("config").document("model_weights").get()

        if doc.exists:
            return doc.to_dict()

        # default fallback
        return {
            "rsi": 1.0,
            "macd": 1.0,
            "ema": 1.0,
            "bb": 1.0,
            "bias": 0.0
        }

    except Exception as e:
        print("❌ Load weights error:", e)
        return {}


# =========================
# 🧠 SAVE WEIGHTS
# =========================
def save_weights(weights):
    try:
        db.collection("config").document("model_weights").set(weights)
        print("🧠 Weights updated")
    except Exception as e:
        print("❌ Save weights error:", e)


# =========================
# ✅ UPDATE SIGNAL
# =========================
def update_signal(doc_id, data):
    try:
        db.collection("signals").document(doc_id).update(data)
    except Exception as e:
        print("❌ Update signal error:", e)