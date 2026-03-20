import os
import json
from datetime import datetime, timezone

import firebase_admin
from firebase_admin import credentials, firestore

db = None

# -------------------------------
# INIT
# -------------------------------

def init_firebase():
    global db

    if firebase_admin._apps:
        db = firestore.client()
        return

    try:
        firebase_key = os.getenv("FIREBASE_KEY")

        if not firebase_key:
            raise Exception("FIREBASE_KEY not found in ENV")

        cred_dict = json.loads(firebase_key)
        cred = credentials.Certificate(cred_dict)

        firebase_admin.initialize_app(cred)
        db = firestore.client()

        print("🔥 Firebase connected")

    except Exception as e:
        print("❌ Firebase init error:", e)
        raise


# -------------------------------
# SAVE SIGNAL
# -------------------------------

def save_signal(signal: dict):
    try:
        signal["timestamp"] = datetime.now(timezone.utc)

        db.collection("signals").add(signal)

    except Exception as e:
        print("❌ Save signal error:", e)


# -------------------------------
# LOAD OPEN SIGNALS
# -------------------------------

def load_open_signals():
    try:
        docs = db.collection("signals") \
            .where("evaluated", "==", False) \
            .stream()

        signals = []
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            signals.append(data)

        print(f"📂 Loaded open signals: {len(signals)}")
        return signals

    except Exception as e:
        print("❌ Load open signals error:", e)
        return []


# -------------------------------
# LOAD ALL SIGNALS
# -------------------------------

def load_all_signals(limit=500):
    try:
        docs = db.collection("signals") \
            .order_by("timestamp", direction=firestore.Query.DESCENDING) \
            .limit(limit) \
            .stream()

        signals = []
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            signals.append(data)

        return signals

    except Exception as e:
        print("❌ Load all signals error:", e)
        return []


# -------------------------------
# UPDATE SIGNAL
# -------------------------------

def update_signal(signal_id, updates: dict):
    try:
        db.collection("signals").document(signal_id).update(updates)
    except Exception as e:
        print("❌ Update signal error:", e)


# -------------------------------
# DELETE (optional)
# -------------------------------

def delete_signal(signal_id):
    try:
        db.collection("signals").document(signal_id).delete()
    except Exception as e:
        print("❌ Delete error:", e)

# -------------------------------
# WEIGHTS (META / AI)
# -------------------------------

def save_weights(weights: dict):
    try:
        db.collection("meta").document("weights").set(weights)
    except Exception as e:
        print("❌ Save weights error:", e)


def load_weights():
    try:
        doc = db.collection("meta").document("weights").get()
        return doc.to_dict() if doc.exists else {}
    except Exception as e:
        print("❌ Load weights error:", e)
        return {}