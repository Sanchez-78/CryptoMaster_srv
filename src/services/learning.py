from src.services.firebase_client import load_weights, save_weights


# =========================
# ⚙️ CONFIG
# =========================

BASE_LR = 0.05
MOMENTUM = 0.9
WEIGHT_CLAMP = 5.0


# =========================
# 🧠 HELPERS
# =========================

def clamp(value, min_val=-WEIGHT_CLAMP, max_val=WEIGHT_CLAMP):
    return max(min(value, max_val), min_val)


def normalize_feature(key, value):
    """
    Normalizace feature → stabilní learning
    """
    if key == "rsi":
        return (value - 50) / 50  # -1 → 1

    if key == "macd":
        return value  # už je relativní

    if key == "ema":
        return value  # už je diff ratio

    if key == "bb":
        return value  # už je normalized pozice

    return value


def compute_adaptive_lr(reward, confidence):
    """
    větší reward + vyšší confidence → větší learning
    """
    return BASE_LR * (1 + abs(reward)) * (0.5 + confidence)


# =========================
# 🎯 MAIN LEARNING FUNCTION
# =========================

def update_model_weights(features: dict, reward: float):
    """
    Hlavní learning funkce (V2)
    """

    try:
        weights = load_weights()

        # init velocity pokud není
        if "_velocity" not in weights:
            weights["_velocity"] = {
                "rsi": 0.0,
                "macd": 0.0,
                "ema": 0.0,
                "bb": 0.0,
                "bias": 0.0,
            }

        velocity = weights["_velocity"]

        confidence = features.get("confidence", 0.5)
        trend = features.get("trend", "SIDEWAYS")

        # adaptive LR
        lr = compute_adaptive_lr(reward, confidence)

        print(f"🧠 Learning → reward: {round(reward,4)}, lr: {round(lr,4)}")

        # =========================
        # 🔄 UPDATE FEATURES
        # =========================

        for key in ["rsi", "macd", "ema", "bb"]:
            if key not in weights:
                continue

            value = features.get(key, 0)

            # normalizace
            value = normalize_feature(key, value)

            # gradient
            grad = reward * value

            # momentum update
            velocity[key] = MOMENTUM * velocity[key] + lr * grad

            weights[key] += velocity[key]

            # clamp
            weights[key] = clamp(weights[key])

        # =========================
        # 🧠 BIAS UPDATE
        # =========================

        bias_grad = reward

        # penalizace proti trendu
        if trend != "SIDEWAYS":
            if (trend == "BULL" and reward < 0) or \
               (trend == "BEAR" and reward < 0):
                bias_grad *= 1.2  # zesílení negativního signálu

        velocity["bias"] = MOMENTUM * velocity["bias"] + lr * bias_grad
        weights["bias"] = clamp(weights.get("bias", 0) + velocity["bias"])

        # =========================
        # 💾 SAVE
        # =========================

        weights["_velocity"] = velocity

        save_weights(weights)

        print("✅ Weights updated")

    except Exception as e:
        print(f"❌ Learning error: {e}")