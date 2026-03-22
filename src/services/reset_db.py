import sys
import os

# 🔥 FIX: přidání root projektu do Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.services.firebase_client import get_db

# kolekce které chceš vymazat
COLLECTIONS = [
    "signals",
    "signals_compressed",
    "meta"
]


def delete_collection(col_name, batch_size=100):
    db = get_db()
    col_ref = db.collection(col_name)

    total_deleted = 0

    while True:
        docs = list(col_ref.limit(batch_size).stream())
        deleted = 0

        for doc in docs:
            doc.reference.delete()
            deleted += 1

        total_deleted += deleted

        print(f"🗑️ {col_name}: deleted {deleted}")

        if deleted < batch_size:
            break

    print(f"✅ {col_name}: TOTAL DELETED {total_deleted}\n")


def reset_firestore():
    print("🔥 RESET FIREBASE START\n")

    for col in COLLECTIONS:
        try:
            delete_collection(col)
        except Exception as e:
            print(f"❌ ERROR in {col}:", e)

    print("🚀 FIREBASE RESET COMPLETE")


if __name__ == "__main__":
    reset_firestore()