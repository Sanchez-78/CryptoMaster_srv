import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

db = None


def init_firebase():
    global db

    if firebase_admin._apps:
        db = firestore.client()
        return

    firebase_key = os.getenv("FIREBASE_KEY")
    cred_dict = json.loads(firebase_key)

    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)

    db = firestore.client()


def get_db():
    global db
    if db is None:
        init_firebase()
    return db


# ---------------- SIGNALS ----------------

def save_signal(signal: dict):
    db = get_db()
    db.collection("signals").add(signal)
    print("✅ Saved:", signal["symbol"], signal["signal"])


def load_all_signals(limit=500):
    db = get_db()
    docs = db.collection("signals").limit(limit).stream()
    return [d.to_dict() for d in docs]


def load_open_signals():
    db = get_db()
    docs = db.collection("signals") \
        .where("evaluated", "==", False) \
        .stream()

    return [(d.id, d.to_dict()) for d in docs]


def update_signal(doc_id, data: dict):
    db = get_db()
    db.collection("signals").document(doc_id).update(data)


# ---------------- 🔥 LEARNING ----------------

def load_recent_trades(limit=100):
    db = get_db()

    docs = db.collection("signals") \
        .where("evaluated", "==", True) \
        .limit(limit) \
        .stream()

    return [d.to_dict() for d in docs]