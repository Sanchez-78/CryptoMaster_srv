import numpy as np

from src.services.firebase_client import load_all_signals


class Retrainer:

    def __init__(self, ml_model):
        self.ml_model = ml_model

    def retrain(self):
        signals = load_all_signals()

        X = []
        y = []
        weights = []

        for s in signals:
            if not s.get("evaluated"):
                continue

            profit = s.get("profit", 0)

            # =========================
            # LABEL
            # =========================
            label = 1 if profit > 0 else 0

            features = s.get("features", {})
            if not features:
                continue

            # =========================
            # VECTOR (ORDERED)
            # =========================
            keys = sorted([k for k, v in features.items() if isinstance(v, (int, float))])
            vector = [features[k] for k in keys]

            if len(vector) < 5:
                continue

            X.append(vector)
            y.append(label)

            # weight podle síly profitu
            weights.append(max(abs(profit), 0.001))

        if len(X) < 10:
            print(f"📊 Samples: {len(X)} → not enough for training")
            return

        print(f"📊 Samples: {len(X)} (+{len(X) - self.ml_model.samples})")

        try:
            X = np.array(X)
            y = np.array(y)

            self.ml_model.model.fit(X, y, sample_weight=np.array(weights))

            self.ml_model.trained = True
            self.ml_model.samples = len(X)

            print("🧠 ML retrained!")

        except Exception as e:
            print("❌ Training error:", e)