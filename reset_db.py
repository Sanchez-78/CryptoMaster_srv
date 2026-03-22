from src.services.firebase_client import get_db

COLLECTIONS = [
    "signals",
    "signals_compressed",
    "meta"
]

def delete_collection(col_name, batch_size=100):
    db = get_db()
    col_ref = db.collection(col_name)

    while True:
        docs = col_ref.limit(batch_size).stream()
        deleted = 0

        for doc in docs:
            doc.reference.delete()
            deleted += 1

        print(f"{col_name}: deleted {deleted}")

        if deleted < batch_size:
            break


if __name__ == "__main__":
    print("🔥 RESET FIREBASE START")

    for c in COLLECTIONS:
        delete_collection(c)

    print("✅ FIREBASE CLEARED")